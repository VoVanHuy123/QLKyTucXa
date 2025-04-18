from rest_framework import serializers
from rooms.models import Room, Building, RoomChangeRequests,RoomAssignments
from account.serializers import UserSerializer
from account.models import Student


class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ['id', 'building_name', 'total_floors']

class RoomAssignmentsSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(),pk_field=serializers.IntegerField(), write_only=True)
    student_detail = UserSerializer(source='student', read_only=True)
    # student = UserSerializer
    class Meta:
        model = RoomAssignments
        fields = ['student','room','bed_number','student_detail',"active"]

class RoomSerializer(serializers.ModelSerializer):
    building = BuildingSerializer
    room_assignments = RoomAssignmentsSerializer(many=True)
    class Meta:
        model = Room
        fields = ['id', 'room_number', 'room_type', 'total_beds', 'available_beds', 'monthly_fee', 'status', 'building','floor','room_assignments']
    


class RoomChangeRequestSerializer(serializers.ModelSerializer):
    student = UserSerializer
    current_room = RoomSerializer
    requested_room = RoomSerializer

    class Meta:
        model = RoomChangeRequests
        fields = ['reason', 'status', 'student', 'current_room', 'requested_room']
