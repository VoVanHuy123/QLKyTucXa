from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, generics, status, parsers, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import authenticate
from oauth2_provider.models import AccessToken, RefreshToken, Application
from oauthlib.common import generate_token
from django.utils.timezone import now
import datetime
from account.models import User, Student
from rooms.models import Room, RoomChangeRequests, RoomAssignments
from account import serializers, paginators, perms, filters
from rooms.serializers import RoomChangeRequestSerializer
from account.serializers import UserSerializer
from KyTucXa import perms

import dotenv
import os

dotenv.load_dotenv()


# dotenv.load_dotenv("/home/vovanhuy/QLKyTucXa/QLKyTucXa/.env")

class UserViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.RetrieveAPIView, generics.ListAPIView):
    queryset = Student.objects.filter(is_active=True)
    serializer_class = serializers.UserSerializer
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser]
    permission_classes = [perms.IsAdminUser]
    pagination_class = paginators.StudentPaginater
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.StudentFillters

    def str_to_bool(self, val):
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            return val.lower() in ['true', '1']
        return False

    @action(methods=['get', 'patch'], url_path="current-user", detail=False,
            permission_classes=[permissions.IsAuthenticated])
    def current_user(self, request):

        if request.method.__eq__("PATCH"):
            u = request.user.student
            data = request.data.copy()
            data.pop("student_code", None)
            data.pop("university", None)

            if 'password' in data:
                u.set_password(data.pop('password'))
            if 'is_first_access' in data:
                data['is_first_access'] = self.str_to_bool(data['is_first_access'])

            avatar = request.FILES.get('avatar')
            if avatar:
                u.avatar = avatar

            serializer = self.serializer_class(u, data=data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializers.UserSerializer(request.user).data)

    @action(methods=['patch'], detail=True)
    def deactivate_student(self, request, pk):
        student = get_object_or_404(Student, pk=pk)
        if student.is_superuser:
            return Response({"error": "Không thể vô hiệu hóa tài khoản admin"}, status=status.HTTP_403_FORBIDDEN)

        student.is_active = False
        student.save()
        return Response({"message": "Đã vô hiệu hóa người dùng thành công!"}, status=status.HTTP_200_OK)

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

        AccessToken.objects.filter(user=user, application=application).delete()
        RefreshToken.objects.filter(user=user, application=application).delete()

        access_token = AccessToken.objects.create(
            user=user,
            application=application,
            token=generate_token(),
            expires=now() + datetime.timedelta(seconds=3600),
            scope="read write"
        )

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

    @action(methods=['get'], detail=False, url_path='available-students')
    def get_available_students(self, request):
        assigned_student_ids = RoomAssignments.objects.filter(active=True).values_list('student_id', flat=True)

        unassigned_students = Student.objects.filter(is_active=True).exclude(id__in=assigned_student_ids)

        return Response(serializers.UserSerializer(unassigned_students, many=True).data)
