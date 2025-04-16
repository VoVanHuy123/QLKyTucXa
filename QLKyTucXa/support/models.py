from django.db import models
from KyTucXa.models import BaseModel
from rooms.models import Room
from account.models import Student, User

class ComplaintsStatus(models.TextChoices):
    PENDING = 'Pending', 'Pending'
    RESOLVED = 'Resolved', 'Resolved'
    
    
class Complaints(BaseModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=ComplaintsStatus.choices)

    class Meta:
        db_table = "complaints"


class ComplaintsResponse(BaseModel):
    complaint = models.ForeignKey('Complaints', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()

    class Meta:
        db_table = "complaints_response"
