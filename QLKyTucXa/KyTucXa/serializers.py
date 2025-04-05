from rest_framework import serializers
from KyTucXa.models import Room,User



class BaseSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        cloud_name = "dnzjjdg0v"
        # data['image'] = f"https://res.cloudinary.com/{cloud_name}/{data['image']}"
        data['image'] = instance.image.url
        return data

class UserSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)

        data['avatar'] = instance.avatar.url if instance.avatar else ''

        return data

# tạo user mới 
    def create(self, validated_data):
        data = validated_data.copy()
        u = User(**data)
        u.role = "Student"
        u.set_password(u.password)
        u.save()

        return u

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password', 'avatar','role','is_staff']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }