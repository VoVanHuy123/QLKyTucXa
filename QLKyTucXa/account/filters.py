# filters.py
import django_filters
from .models import Student
from django.db.models import Q

class StudentFillters(django_filters.FilterSet):
    # building_id = django_filters.NumberFilter(field_name="building__id")
    name = django_filters.CharFilter(method='filter_full_name')

    class Meta:
        model = Student
        fields = ['name']

    def filter_full_name(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value) | Q(last_name__icontains=value)
        )

   