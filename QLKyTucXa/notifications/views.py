from django.shortcuts import render
from rest_framework import viewsets,generics,permissions,status
from .models import Notification
from .serializers import NotiSerializers
from rest_framework.decorators import action
from KyTucXa.perms import IsAdminOrReadOnly
from .paginators import NotiPaginater
from config.PushNoti import send_push_notification
from account.models import User
from rest_framework.response import Response
# Create your views here.
class NotiViewSet(viewsets.ViewSet,generics.ListAPIView,generics.CreateAPIView,generics.RetrieveAPIView):
    queryset = Notification.objects.filter(active = True)
    serializer_class = NotiSerializers
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = NotiPaginater

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notification = serializer.save()

        if notification.is_urgent:
            users = User.objects.exclude(expo_token=None).exclude(expo_token="")

            for user in users:
                send_push_notification(
                    user.expo_token,
                    notification.title,
                    notification.content
                )

        return Response(serializer.data, status=status.HTTP_201_CREATED)