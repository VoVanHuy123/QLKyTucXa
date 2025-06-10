from rest_framework import serializers
from support.models import Complaints, ComplaintsStatus, ComplaintsResponse
from account.serializers import UserSerializer
from rooms.serializers import RoomSerializer


class ComplaintsResponseSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = UserSerializer(instance.user).data
        return data

    class Meta:
        model = ComplaintsResponse
        fields = ['id', 'created_date', 'update_date', 'content', 'user', 'complaint']
        extra_kwargs = {
            'complaint': {
                'write_only': True
            }
        }


class ComplaintsSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['student'] = UserSerializer(instance.student).data
        data['room'] = RoomSerializer(instance.room).data
        data['image'] = instance.image.url if instance.image else ''
        return data

    class Meta:
        model = Complaints
        fields = ["id", "student", 'room', 'image', "title", "description", "image", "status", "created_date"]
        read_only_fields = ('status',)
