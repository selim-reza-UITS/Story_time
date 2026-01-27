from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()
# Create your models here.


class TeacherProfile(models.Model):
    GRADE_CHOICES = [
        (3, 'Grade 3'),
        (4, 'Grade 4'),
        (5, 'Grade 5'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    grade_level = models.IntegerField(choices=GRADE_CHOICES, default=1)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"Teacher: {self.user.username}"