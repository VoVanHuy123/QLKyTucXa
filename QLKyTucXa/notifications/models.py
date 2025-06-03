from django.db import models
from KyTucXa.models import BaseModel
from rooms.models import Room


class Notification(BaseModel):
    title = models.CharField(max_length=255)
    content = models.TextField()
    announcement_type = models.CharField(max_length=50, null=True)
    is_urgent = models.BooleanField(default=False, null=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ['-created_date']
        db_table = "notification"
