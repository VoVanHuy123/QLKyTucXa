from rest_framework import serializers
from KyTucXa.models import Room,User,Building


class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ['id','building_name','total_floors']
class RoomSerializer(serializers.ModelSerializer):
    building = BuildingSerializer
    class Meta:
        model = Room
        fields = ['id','room_number','room_type','total_beds','available_beds','monthly_fee','status','building']
