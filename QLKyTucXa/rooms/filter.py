# filters.py
import django_filters
from rooms.models import Room,RoomChangeRequests,RoomAssignments

class RoomFilter(django_filters.FilterSet):
    building = django_filters.NumberFilter(field_name="building__id")
    floor = django_filters.NumberFilter(field_name="floor")
    room_number = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Room
        fields = ['building', 'floor', 'room_number']

    class Meta:
        model = Room
        fields = ['building_id', 'room_number']


class RoomChangeRequestFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(lookup_expr='exact')

    class Meta:
        model = RoomChangeRequests
        fields = ['status']
class RoomAssignmentFilter(django_filters.FilterSet):
    active = django_filters.CharFilter(lookup_expr='exact')
    student = django_filters.CharFilter(lookup_expr='exact')

    class Meta:
        model = RoomAssignments
        fields = ['active','student']
