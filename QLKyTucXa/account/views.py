from pickle import FALSE

from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, generics, status, parsers, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.parsers import JSONParser

from oauth2_provider.models import AccessToken, RefreshToken, Application
from oauthlib.common import generate_token
from django.utils.timezone import now
import datetime

from account.models import User
from rooms.models import Room, RoomChangeRequests
from account import serializers, paginators, perms
from rooms.serializers import RoomChangeRequestSerializer
from account.serializers import UserSerializer
import dotenv
import os

dotenv.load_dotenv()


# treen pythonanywhere bật cái này lên
# dotenv.load_dotenv("/home/vovanhuy/QLKyTucXa/QLKyTucXa/.env")

# Create your views here.


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.RetrieveAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = serializers.UserSerializer
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser]

    # /user/current-user/
    @action(methods=['get', 'patch'], url_path="current-user", detail=False,
            permission_classes=[permissions.IsAuthenticated])
    def get_curent_user(self, request):

        if request.method.__eq__("PATCH"):
            u = request.user
            for key in request.data:
                if key in ['first_name', 'last_name', 'username', 'is_first_access', 'role']:
                    setattr(u, key, request.data[key])
                elif key == 'password':
                    u.set_password(request.data[key])
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
        invoices = RoomChangeRequests.objects.filter(user_id=pk)
        return Response(RoomChangeRequestSerializer(invoices, many=True).data)

    @action(methods=['post'], detail=False)
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response({"error": "Missing username or password"}, status=400)

        user = authenticate(username=username, password=password)
        if user is None:
            return Response({"error": "Invalid credentials"}, status=400)

        CLIENT_ID = os.getenv('CLIENT_ID')
        # CLIENT_SECRET = os.getenv('CLIENT_SECRET')

        # # Gửi request lấy access token từ OAuth2 Provider
        # data = {
        #     "grant_type": "password",
        #     "username": username,
        #     "password": password,
        #     "client_id": CLIENT_ID,
        #     "client_secret": CLIENT_SECRET,
        # }
        # response = requests.post("http://127.0.0.1:8000/o/token/", json=data)

        # return Response(response.json(), status=response.status_code)
        # Lấy ứng dụng OAuth2
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

        return Response({
            "access_token": access_token.token,
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": refresh_token.token,
            "user": UserSerializer(user).data
        })
