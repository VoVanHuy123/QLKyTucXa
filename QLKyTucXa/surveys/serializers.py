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
        fields = ["question","survey","student","answer"]
        extra_kwargs = {
            'survey': {'write_only': True},
            'student': {'write_only': True},
        }
class SurveySerializer(serializers.ModelSerializer):
    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     data['user'] = UserSerializer(instance.user).data
    #     return data
    user  = UserSerializer(read_only=True)
    # questions = SurveyQuestionSerializer(many=True)
    class Meta:
        model = Survey
        fields = ['id','title', 'description','user', 'created_date',"questions"]
        extra_kwargs = {
            'questions': {'write_only': True,
                            'required': False}
        }
        
    
    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        user = self.context['request'].user
        survey = Survey.objects.create(user=user, **validated_data)

        # for question in questions_data:
        #     SurveyQuestion.objects.create(survey=survey, **question)

        return survey

    # def update(self, instance, validated_data):
    #     questions_data = validated_data.pop('questions', [])

    #     # Cập nhật trường của survey
    #     instance.title = validated_data.get('title', instance.title)
    #     instance.description = validated_data.get('description', instance.description)
    #     instance.save()

    #     existing_ids = [q.id for q in instance.questions.all()]
    #     sent_ids = []

    #     for question_data in questions_data:
    #         question_id = question_data.get('id', None)
    #         if question_id:
    #             sent_ids.append(question_id)
    #             try:
    #                 question_instance = SurveyQuestion.objects.get(id=question_id, survey=instance)
    #                 question_instance.question_text = question_data.get('question_text', question_instance.question_text)
    #                 question_instance.question_type = question_data.get('question_type', question_instance.question_type)
    #                 question_instance.save()
    #             except SurveyQuestion.DoesNotExist:
    #                 continue  # hoặc raise ValidationError nếu muốn
    #         else:
    #             SurveyQuestion.objects.create(survey=instance, **question_data)

    #     # Tuỳ chọn: Xoá các câu hỏi không còn trong request
    #     for old_id in existing_ids:
    #         if old_id not in sent_ids:
    #             SurveyQuestion.objects.filter(id=old_id).delete()

    #     return instance
