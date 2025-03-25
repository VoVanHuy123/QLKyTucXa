from rest_framework import serializers
from KyTucXa.models import RoomChangeRequests
from KyTucXa.serializers import UserSerializer
from rooms.serializers  import RoomSerializer

class RoomChangeRequestSerializer(serializers.ModelSerializer):
    student = UserSerializer
    current_room = RoomSerializer
    requested_room = RoomSerializer
    class Meta:
        model = RoomChangeRequests
        fields = ['reason','status','student','current_room','requested_room']
    pass

