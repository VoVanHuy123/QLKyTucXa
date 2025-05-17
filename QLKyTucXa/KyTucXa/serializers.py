from rest_framework import serializers


class BaseSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        cloud_name = "dnzjjdg0v"
        # data['image'] = f"https://res.cloudinary.com/{cloud_name}/{data['image']}"
        data['image'] = instance.image.url if instance.image else ''
        return data
