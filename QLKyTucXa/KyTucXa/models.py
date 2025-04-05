from django.db import models

# Create your models here.
from importlib.metadata import requires

# Create your models here.
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField

# việc đâu tiên
class User(AbstractUser):
    ROLE_CHOICES = [
        ('Student', 'Student'),
        ('Admin', 'Administrator')
    ]
    avatar = CloudinaryField(blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
   

class BaseModel(models.Model):
    active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-id']

class Building(BaseModel):
    building_name = models.CharField(max_length=50)
    total_floors = models.IntegerField()
    def __str__(self):
        return self.building_name

class Room(BaseModel):
    STATUS_CHOICES = [
        ('Empty','Empty'),
        ('Full', 'Full')
    ]
    building = models.ForeignKey('Building', on_delete=models.CASCADE)
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=50, null=True)
    floor = models.IntegerField(null=True)
    total_beds = models.IntegerField()
    available_beds = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,default='Empty')
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return self.room_number

class Student(User):
    phone_number = models.IntegerField(null=False)
    # thuộc tính room chuyển về null khi Room bị xóa model.SET_NULL
    room = models.ForeignKey('Room', on_delete=models.SET_NULL, null=True, blank=True,related_name='students')

class RoomAssignments(BaseModel):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    room = models.ForeignKey('Room', on_delete=models.CASCADE)
    bed_number = models.IntegerField()

class RoomChangeRequests(BaseModel):
    STARTUS_CHOICES = [('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')]
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    current_room = models.ForeignKey('Room', related_name='current_room', on_delete=models.CASCADE)
    requested_room = models.ForeignKey('Room', related_name='requested_room', on_delete=models.CASCADE)
    reason = models.CharField(max_length=500)
    status = models.CharField(max_length=50, choices=STARTUS_CHOICES, default='Pending')

class Invoice(BaseModel):
    STATUS_CHOICES = [
        ('Unpaid', 'Unpaid'),
        ('Paid', 'Paid')
    ]
    description = models.CharField(max_length=100,null=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    # amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    def __str__(self):
        return self.description

class InvoiceItems(models.Model):
    invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE)
    description = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return self.description

class Notification(BaseModel):
    title = models.CharField(max_length=255)
    content = models.TextField()
    announcement_type = models.CharField(max_length=50,null=True)

class Complaints(BaseModel):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Resolved', 'Resolved')
    ]
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    room = models.ForeignKey('Room', on_delete=models.CASCADE)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

class ComplaintsResponse(BaseModel):
    complaint = models.ForeignKey('Complaints', on_delete=models.CASCADE)
    user = models.ForeignKey('User',on_delete=models.CASCADE)
    content = models.TextField()

class Survey(BaseModel):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    user = models.ForeignKey('User', on_delete=models.CASCADE)

class SurveyQuestion(BaseModel):
    survey = models.ForeignKey('Survey', on_delete=models.CASCADE)
    question_text = models.CharField(max_length=500)
    question_type = models.CharField(max_length=50)

class SurveyResponse(BaseModel):
    survey = models.ForeignKey('Survey', on_delete=models.CASCADE)
    question = models.ForeignKey('SurveyQuestion', on_delete=models.CASCADE)
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    answer = models.CharField(max_length=500)

class Chat(BaseModel):
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='student_messages')
    admin = models.ForeignKey('User', on_delete=models.CASCADE, related_name='admin_messages')
    message = models.TextField()