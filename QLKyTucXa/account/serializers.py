from rest_framework import serializers
from .models import User, Student


class UserSerializer(serializers.ModelSerializer):
    student_code = serializers.CharField(write_only=True)
    university = serializers.CharField(write_only=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data['avatar'] = instance.avatar.url if instance.avatar else ''

        if hasattr(instance, 'student'):
            student = instance.student
            data['student_code'] = student.student_code
            data['university'] = student.university

        return data

    def create(self, validated_data):
        data = validated_data.copy()
        u = Student(**data)
        u.role = "Student"
        u.is_staff = False
        u.set_password(u.password)
        u.save()

        return u

    class Meta:
        model = Student
        fields = ['id', 'first_name', 'last_name', 'email', 'username', 'password', 'avatar', 'role', 'is_staff',
                  "is_first_access", 'student_code', 'university', 'phone_number']
        extra_kwargs = {
            'password': {
                'write_only': True
            },
        }
        read_only_fields = ('is_staff', 'role')
