from rest_framework import serializers
from .models import Survey, SurveyResponse, SurveyQuestion
from account.serializers import UserSerializer


class SurveyQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyQuestion
        fields = "__all__"
        extra_kwargs = {
            'survey': {
                'write_only': True,
                'required': False
            },
        }


class SurveyResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyResponse
        fields = ["question", "survey", "student", "answer"]
        extra_kwargs = {
            'survey': {'write_only': True},
            'student': {'write_only': True},
        }


class SurveySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Survey
        fields = ['id', 'title', 'description', 'user', 'created_date', "questions"]
        extra_kwargs = {
            'questions': {'write_only': True,
                          'required': False}
        }

    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        user = self.context['request'].user
        survey = Survey.objects.create(user=user, **validated_data)

        return survey
