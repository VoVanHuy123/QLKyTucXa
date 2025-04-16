# filters.py
import django_filters
from .models import Invoice

class InvoicesFilter(django_filters.FilterSet):
    room = django_filters.NumberFilter(field_name="room_id")

    class Meta:
        model = Invoice
        fields = ['room_id']