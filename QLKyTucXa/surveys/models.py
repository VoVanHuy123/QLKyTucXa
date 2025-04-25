from django.db import models
from KyTucXa.models import BaseModel
from account.models import User, Student


class Survey(BaseModel):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "survey"


class SurveyQuestion(BaseModel):
    survey = models.ForeignKey('Survey', on_delete=models.CASCADE, related_name='questions')
    question_text = models.CharField(max_length=500)
    question_type = models.CharField(max_length=50)

    class Meta:
        db_table = "survey_questions"


class SurveyResponse(BaseModel):
    survey = models.ForeignKey('Survey', on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey('SurveyQuestion', on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    answer = models.CharField(max_length=500)

    class Meta:
        db_table = "survey_response"
        constraints = [
            models.UniqueConstraint(
                fields=['question', 'student'],
                name='unique_question_student'
            )
        ]
