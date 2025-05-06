
# Create your models here.
from django.db import models
from KyTucXa.models import BaseModel
from KyTucXa.models import Room, Building

class LocationType(models.TextChoices):
    BUILDING = 'building', 'Building'
    ROOM = 'room', 'Room'
    PARKING = 'parking', 'Parking'
    OTHER = 'other', 'Other'

class Location(BaseModel):
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    description = models.TextField(blank=True, null=True)
    location_type = models.CharField(max_length=50, choices=LocationType.choices)
    building = models.ForeignKey(Building, on_delete=models.SET_NULL, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "location"
