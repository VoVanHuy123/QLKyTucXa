from django.db import models
from KyTucXa.models import BaseModel
from rooms.models import Room
from account.models import Student, User
from cloudinary.models import CloudinaryField


class ComplaintsStatus(models.TextChoices):
    PENDING = 'Pending', 'Pending'
    RESOLVED = 'Resolved', 'Resolved'
    
    
class Complaints(BaseModel):
    student = models.ForeignKey(Student, null=False, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, null=False, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, null=False)
    description = models.TextField(null=False)
    image = CloudinaryField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=ComplaintsStatus.choices, default=ComplaintsStatus.PENDING)

    class Meta:
        db_table = "complaints"


class ComplaintsResponse(BaseModel):
    complaint = models.ForeignKey('Complaints', on_delete=models.CASCADE, related_name="responses")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()

    class Meta:
        db_table = "complaints_response"
