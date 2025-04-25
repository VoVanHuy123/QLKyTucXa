from rest_framework import serializers
from .models import Survey, SurveyResponse, SurveyQuestion
from account.serializers import UserSerializer


class SurveySerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = UserSerializer(instance.user).data
        return data

    class Meta:
        model = Survey
        fields = "__all__"


class SurveyQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyQuestion
        fields = "__all__"
        extra_kwargs = {
            'survey': {
                'write_only': True,
            },
        }


class SurveyResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyResponse
        fields = "__all__"
