from rest_framework import serializers
from KyTucXa.models import Room,User

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id','room_number','room_type','total_beds','available_beds']

