from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField


class User(AbstractUser):
    ROLE_CHOICES = [
        ('Student', 'Student'),
        ('Admin', 'Administrator')
    ]
    avatar = CloudinaryField(blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_first_access = models.BooleanField(default=True)
    class Meta:
        db_table = "user"


class Student(User):
    phone_number = models.IntegerField(null=True)
    student_code = models.CharField(max_length=20, null=True)
    university = models.CharField(max_length=20, null=True)

    class Meta:
        db_table = 'student'
