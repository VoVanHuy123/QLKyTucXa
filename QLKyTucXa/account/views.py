from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, generics, status, parsers, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate
from oauth2_provider.models import AccessToken, RefreshToken, Application
from oauthlib.common import generate_token
from django.utils.timezone import now
import datetime
from account.models import User, Student
from rooms.models import Room, RoomChangeRequests, RoomAssignments
from account import serializers, paginators, perms
from rooms.serializers import RoomChangeRequestSerializer
from account.serializers import UserSerializer
from KyTucXa import perms
import dotenv
import os

dotenv.load_dotenv()


# treen pythonanywhere bật cái này lên
# dotenv.load_dotenv("/home/vovanhuy/QLKyTucXa/QLKyTucXa/.env")

# Create your views here.


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.RetrieveAPIView):
    queryset = Student.objects.filter(is_active=True)
    serializer_class = serializers.UserSerializer
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser]
    permission_classes = [perms.IsAdminUser]

    def str_to_bool(self, val):
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            return val.lower() in ['true', '1']
        return False

    # /user/current-user/
    @action(methods=['get', 'patch'], url_path="current-user", detail=False,
            permission_classes=[permissions.IsAuthenticated])
    def current_user(self, request):

        if request.method.__eq__("PATCH"):
            u = request.user

            student = None
            if hasattr(u, 'student'):
                student = u.student

            for key in request.data:
                if key in ['first_name', 'last_name', 'username', 'role', 'email']:
                    setattr(u, key, request.data[key])
                elif key == 'is_first_access':
                    setattr(u, key, self.str_to_bool(request.data[key]))
                elif key == 'password':
                    u.set_password(request.data[key])
                elif student and key in ['phone_number']:
                    setattr(student, key, request.data[key])

            avatar = request.FILES.get('avatar')
            if avatar:
                u.avatar = avatar

            if student:
                student.save()
            u.save()
            return Response(serializers.UserSerializer(u).data)
        else:
            return Response(serializers.UserSerializer(request.user).data)

    # /user/{id}/delete-user/
    @action(methods=['delete'], detail=True, permission_classes=[permissions.IsAdminUser])
    def delete_user(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user.is_superuser:
            return Response({"error": "Không thể xóa tài khoản admin"}, status=status.HTTP_403_FORBIDDEN)
        user.delete()
        return Response({"message": "Xóa người dùng thành công!"}, status=status.HTTP_204_NO_CONTENT)

    # /user/{id}/requests/
    @action(methods=['get'], detail=True, url_path="requests")
    def get_invoices(self, request, pk):
        roomRequests = RoomChangeRequests.objects.filter(user_id=pk)
        return Response(RoomChangeRequestSerializer(roomRequests, many=True).data)

    @action(methods=['post'], detail=False, permission_classes=[])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        expo_token = request.data.get('expo_token')
        if not username or not password:
            return Response({"error": "Missing username or password"}, status=400)

        user = authenticate(username=username, password=password)
        if user is None:
            return Response({"error": "Sai tên đăng nhập hoặc mật khẩu"}, status=status.HTTP_401_UNAUTHORIZED)

        CLIENT_ID = os.getenv('CLIENT_ID')
        try:
            application = Application.objects.get(client_id=CLIENT_ID)
        except Application.DoesNotExist:
            return Response({"error": "OAuth2 Application not found"}, status=500)

        # Xóa token cũ (nếu có)
        AccessToken.objects.filter(user=user, application=application).delete()
        RefreshToken.objects.filter(user=user, application=application).delete()

        # Tạo access token mới
        access_token = AccessToken.objects.create(
            user=user,
            application=application,
            token=generate_token(),
            expires=now() + datetime.timedelta(seconds=3600),
            scope="read write"
        )

        # Tạo refresh token mới
        refresh_token = RefreshToken.objects.create(
            user=user,
            application=application,
            token=generate_token(),
            access_token=access_token
        )
        if expo_token and expo_token != user.expo_token:
            user.expo_token = expo_token
            user.save()
        return Response({
            "access_token": access_token.token,
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": refresh_token.token,
            "user": UserSerializer(user).data
        })

    @action(methods=['get'], detail=False, url_path='available-students',
            permission_classes=[permissions.IsAuthenticated])
    def get_available_students(self, request):
        # Lấy ID sinh viên đang có phòng (RoomAssignments còn active)
        assigned_student_ids = RoomAssignments.objects.filter(active=True).values_list('student_id', flat=True)

        # Sinh viên đang hoạt động nhưng chưa có phòng hiện tại
        unassigned_students = Student.objects.filter(is_active=True).exclude(id__in=assigned_student_ids)

        return Response(serializers.UserSerializer(unassigned_students, many=True).data)

    # @action(methods=['post'], detail=False, url_path='update-token',
    #         permission_classes=[permissions.IsAuthenticated])
    # def update_token(self, request):
    #     token = request.data.get("expo_token")
    #     if token:
    #         request.user.expo_token = token
    #         request.user.save()
    #         return Response({"message": "Token saved successfully", "expo_token": request.user.expo_token})
    #     return Response({"error": "No token provided"}, status=400)
