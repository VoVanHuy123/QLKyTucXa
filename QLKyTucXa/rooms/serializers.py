from rest_framework import serializers
from rooms.models import Room, Building, RoomChangeRequests, RoomAssignments
from account.serializers import UserSerializer
from account.models import Student


class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ['id', 'building_name', 'total_floors']


class RoomAssignmentsSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), pk_field=serializers.IntegerField(),
                                                 write_only=True)
    student_detail = UserSerializer(source='student', read_only=True)

    class Meta:
        model = RoomAssignments
        fields = ['id', 'student', 'room', 'bed_number', 'student_detail', "active"]


class RoomSerializer(serializers.ModelSerializer):
    building = BuildingSerializer()

    class Meta:
        model = Room
        fields = ['id', 'room_number', 'room_type', 'total_beds', 'available_beds', 'monthly_fee', 'status', 'building',
                  'floor']


class RoomChangeRequestSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    current_room = serializers.PrimaryKeyRelatedField(read_only=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data['current_room'] = RoomSerializer(instance.current_room).data
        data['requested_room'] = RoomSerializer(instance.requested_room).data
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        if request and not request.user.is_staff:
            validated_data.pop('status', None)

        return super().create(validated_data)

    class Meta:
        model = RoomChangeRequests
        fields = ['id', 'reason', 'status', 'student', 'current_room', 'requested_room', 'created_date']
