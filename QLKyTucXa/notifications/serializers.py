from rest_framework import serializers
from notifications.models import Notification


class NotiSerializers(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'title', 'content', 'created_date', 'update_date','is_urgent','announcement_type')
