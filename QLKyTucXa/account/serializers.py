from rest_framework import serializers
from .models import User,Student


class UserSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)

        data['avatar'] = instance.avatar.url if instance.avatar else ''

        return data

    # tạo user mới
    def create(self, validated_data):
        data = validated_data.copy()
        u = Student(**data)
        u.role = "Student"
        u.set_password(u.password)
        u.save()

        return u

    class Meta:
        model = Student
        fields = ['id','first_name', 'last_name', 'username', 'password', 'avatar', 'role', 'is_staff',"is_first_access","phone_number","student_code","university"]
        extra_kwargs = {
            'password': {
                'write_only': True,
                
            },
            # 'is_first_access': {'required': False}
        
        }
