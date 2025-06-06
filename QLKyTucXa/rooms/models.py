from django.core.exceptions import ValidationError
from django.db import models
from django_mysql.models import EnumField

from KyTucXa.models import BaseModel
from account.models import Student


class Building(BaseModel):
    building_name = models.CharField(max_length=50, unique=True)
    total_floors = models.IntegerField()

    def __str__(self):
        return self.building_name

    class Meta:
        db_table = "building"


class RoomStatus(models.TextChoices):
    EMPTY = 'Empty', 'Empty'
    FULL = 'Full', 'Full'


class Room(BaseModel):
    building = models.ForeignKey('Building', on_delete=models.CASCADE, related_name="rooms")
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=50, null=True)
    floor = models.IntegerField(null=True)
    total_beds = models.IntegerField()
    available_beds = models.IntegerField()
    status = EnumField(choices=RoomStatus.choices, default=RoomStatus.EMPTY)
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.room_number

    @property
    def room_assignments_active(self):
        return self.room_assignments.filter(active=True)

    class Meta:
        db_table = "room"


class RoomAssignments(BaseModel):
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="room_assignments")
    room = models.ForeignKey('Room', on_delete=models.PROTECT, related_name="room_assignments")
    bed_number = models.IntegerField(null=True)

    class Meta:
        db_table = "room_assignments"

    def clean(self):
        if self.active:
            check = RoomAssignments.objects.filter(student=self.student, active=True)
            if self.pk:
                check = check.exclude(pk=self.pk)
            if check.exists():
                raise ValidationError("Sinh viên đã có phòng")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class RoomChangeStatus(models.TextChoices):
    PENDING = 'Pending', 'Pending'
    APPROVED = 'Approved', 'Approved'
    REJECTED = 'Rejected', 'Rejected'


class RoomChangeRequests(BaseModel):
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    current_room = models.ForeignKey('Room', related_name='current_room', on_delete=models.PROTECT)
    requested_room = models.ForeignKey('Room', related_name='requested_room', on_delete=models.PROTECT)
    reason = models.CharField(max_length=500)
    status = EnumField(choices=RoomChangeStatus.choices, default=RoomChangeStatus.PENDING)

    class Meta:
        db_table = "room_change_requests"
