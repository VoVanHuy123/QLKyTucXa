from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField


class UserRole(models.TextChoices):
    STUDENT = 'Student', 'Student'
    ADMIN = 'Admin', 'Admin'


class User(AbstractUser):
    avatar = CloudinaryField(blank=True, null=True)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.STUDENT)
    is_first_access = models.BooleanField(default=True)
    expo_token = models.CharField(max_length=255, blank=True, null=True)
    class Meta:
        db_table = "user"


class Student(User):
    phone_number = models.CharField(max_length=20,null=True)
    student_code = models.CharField(max_length=20, null=True)
    university = models.CharField(max_length=20, null=True)

    class Meta:
        db_table = 'student'
