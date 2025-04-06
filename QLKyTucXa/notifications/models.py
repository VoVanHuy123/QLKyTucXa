from django.db import models
from KyTucXa.models import BaseModel


class Notification(BaseModel):
    title = models.CharField(max_length=255)
    content = models.TextField()
    announcement_type = models.CharField(max_length=50,null=True)

    class Meta:
        db_table = "notification"