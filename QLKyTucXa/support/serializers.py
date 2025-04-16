from rest_framework import serializers
from support.models import Complaints, ComplaintsStatus, ComplaintsResponse

class ComplaintsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaints
        fields = ['id', 'created_date', 'update_date', 'description', 'status','room_id', "student_id"]

class ComplaintsResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintsResponse
        fields = ['id', 'created_date', 'update_date', 'content', 'user_id']
