from rest_framework import serializers
from KyTucXa.models import Room,User

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id','room_number','room_type','total_beds','available_beds']

class UserSelializer(serializers.ModelSerializer):
    class Meta:
        model = User

class BaseSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        cloud_name = "dnzjjdg0v"
        # data['image'] = f"https://res.cloudinary.com/{cloud_name}/{data['image']}"
        data['image'] = instance.image.url
        return data

