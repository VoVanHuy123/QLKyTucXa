from django.shortcuts import render
from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from KyTucXa.models import RoomChangeRequests
from support import serializers

# Create your views here.
class RoomChangeRequestViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.RetrieveAPIView,generics.UpdateAPIView):
    queryset = RoomChangeRequests.objects.filter(active=True)
    serializer_class = serializers.RoomChangeRequestSerializer
    permission_classes = permissions.IsAuthenticated

    