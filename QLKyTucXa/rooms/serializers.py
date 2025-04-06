from rest_framework import serializers
from rooms.models import Room, Building, RoomChangeRequests
from account.serializers import UserSerializer


class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ['id', 'building_name', 'total_floors']


class RoomSerializer(serializers.ModelSerializer):
    building = BuildingSerializer

    class Meta:
        model = Room
        fields = ['id', 'room_number', 'room_type', 'total_beds', 'available_beds', 'monthly_fee', 'status', 'building']


class RoomChangeRequestSerializer(serializers.ModelSerializer):
    student = UserSerializer
    current_room = RoomSerializer
    requested_room = RoomSerializer

    class Meta:
        model = RoomChangeRequests
        fields = ['reason', 'status', 'student', 'current_room', 'requested_room']
