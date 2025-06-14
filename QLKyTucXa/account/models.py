from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField
from django_mysql.models import EnumField


class UserRole(models.TextChoices):
    STUDENT = 'Student', 'Student'
    ADMIN = 'Admin', 'Admin'


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=10, unique=True, validators=[
        RegexValidator(
            regex=r'^\d{10}$',
            message='Số điện thoại phải đúng 10 chữ số',
        )
    ])
    avatar = CloudinaryField(blank=True, null=True)
    role = EnumField(choices=UserRole.choices, default=UserRole.STUDENT)
    is_first_access = models.BooleanField(default=True)
    expo_token = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "user"


class Student(User):
    student_code = models.CharField(max_length=20)
    university = models.CharField(max_length=20)

    def save(self, *args, **kwargs):
        if self.pk:
            old = Student.objects.get(pk=self.pk)
            if old.is_active and not self.is_active:

                latest_active_assignment = self.room_assignments.filter(active=True).order_by('-created_date').first()

                if latest_active_assignment:
                    room = latest_active_assignment.room
                    room.available_beds += 1
                    room.status = "Empty"

                    room.save()

                    latest_active_assignment.active = False
                    latest_active_assignment.save()

        super().save(*args, **kwargs)

    class Meta:
        db_table = 'student'
        constraints = [
            models.UniqueConstraint(
                fields=['student_code', 'university'],
                name='unique_student_code_university'
            )
        ]
