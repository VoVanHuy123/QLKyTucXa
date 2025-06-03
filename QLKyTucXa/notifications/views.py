from django.db.models import Q
from django.shortcuts import render
from rest_framework import viewsets, generics, permissions, status

from rooms.models import RoomAssignments
from .models import Notification
from .serializers import NotiSerializers
from rest_framework.decorators import action
from KyTucXa.perms import IsAdminOrReadOnly
from .paginators import NotiPaginater
from config.PushNoti import send_push_notification
from account.models import User
from rest_framework.response import Response


# Create your views here.
class NotiViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView, generics.RetrieveAPIView):
    queryset = Notification.objects
    serializer_class = NotiSerializers
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = NotiPaginater

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user

        noti_filters = Q(active=True)

        q = self.request.query_params.get('q')
        room_param = self.request.query_params.get('room')

        if not user.is_staff:
            try:
                assignment = RoomAssignments.objects.get(student=user.student, active=True)
                if room_param:
                    noti_filters &= Q(room=assignment.room)
                else:
                    noti_filters &= Q(room__isnull=True) | Q(room=assignment.room)
            except Exception:
                noti_filters &= Q(room__isnull=True)

        if q and q.lower() != "all":
            noti_filters &= Q(announcement_type=q)

        return queryset.filter(noti_filters)

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
