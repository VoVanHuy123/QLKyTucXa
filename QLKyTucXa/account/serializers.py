from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)

        data['avatar'] = instance.avatar.url if instance.avatar else ''

        if hasattr(instance, 'student'):
            student = instance.student
            data['phone_number'] = student.phone_number
            data['student_code'] = student.student_code
            data['university'] = student.university

        return data

    # tạo user mới
    def create(self, validated_data):
        data = validated_data.copy()
        u = User(**data)
        u.role = "Student"
        u.is_staff = False
        u.set_password(u.password)
        u.save()

        return u

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password', 'avatar', 'role', 'is_staff',"is_first_access"]
        extra_kwargs = {
            'password': {
                'write_only': True,
                
            },
            # 'is_first_access': {'required': False}
        
        }
