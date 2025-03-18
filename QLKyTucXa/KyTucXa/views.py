from django.shortcuts import render
from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response

from KyTucXa.models import Room
from KyTucXa.serializers import RoomSerializer
from KyTucXa import paginators

# Create your views here.
class RoomViewSet(viewsets.ViewSet,generics.ListAPIView):
    queryset = Room.objects.filter(status='Empty')
    serializer_class = RoomSerializer
    
