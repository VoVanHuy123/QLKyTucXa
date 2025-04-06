from rest_framework import serializers
from notifications.models import Notification


class NotiSerializers(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'title', 'content', 'created_at', 'updated_at')
