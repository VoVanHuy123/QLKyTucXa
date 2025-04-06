from django.db import models
from KyTucXa.models import BaseModel
from account.models import Student


class Building(BaseModel):
    building_name = models.CharField(max_length=50)
    total_floors = models.IntegerField()

    def __str__(self):
        return self.building_name

    class Meta:
        db_table = "building"


class Room(BaseModel):
    STATUS_CHOICES = [
        ('Empty', 'Empty'),
        ('Full', 'Full')
    ]
    building = models.ForeignKey('Building', on_delete=models.CASCADE)
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=50, null=True)
    floor = models.IntegerField(null=True)
    total_beds = models.IntegerField()
    available_beds = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Empty')
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.room_number

    class Meta:
        db_table = "room"


class RoomAssignments(BaseModel):
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    room = models.ForeignKey('Room', on_delete=models.PROTECT)
    bed_number = models.IntegerField()

    class Meta:
        db_table = "room_assignments"


class RoomChangeRequests(BaseModel):
    STATUS_CHOICES = [('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')]
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    current_room = models.ForeignKey('Room', related_name='current_room', on_delete=models.PROTECT)
    requested_room = models.ForeignKey('Room', related_name='requested_room', on_delete=models.PROTECT)
    reason = models.CharField(max_length=500)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')

    class Meta:
        db_table = "room_change_requests"
