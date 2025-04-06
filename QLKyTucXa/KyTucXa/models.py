from django.db import models

class BaseModel(models.Model):
    active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-id']


# class Chat(BaseModel):
#     student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='student_messages')
#     admin = models.ForeignKey('User', on_delete=models.CASCADE, related_name='admin_messages')
#     message = models.TextField()
