# filters.py
import django_filters
from KyTucXa.models import Room

class RoomFilter(django_filters.FilterSet):
    building_id = django_filters.NumberFilter(field_name="building__id")
    room_number = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Room
        fields = ['building_id', 'room_number']