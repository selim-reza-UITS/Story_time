from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Base User model to distinguish between roles.
    Using email as the primary login field is recommended for modern platforms.
    """
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_admin_user = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class StudentProfile(models.Model):
    GRADE_CHOICES = [
        (3, 'Grade 3'),
        (4, 'Grade 4'),
        (5, 'Grade 5'),
    ]

    PROFICIENCY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    grade_level = models.IntegerField(choices=GRADE_CHOICES, default=1)
    vocabulary_proficiency = models.CharField(
        max_length=20, 
        choices=PROFICIENCY_CHOICES, 
        default='beginner'
    )
    assigned_teacher = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='my_students'
    )
    
    total_books_read = models.PositiveIntegerField(default=0)
    words_learned = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - Grade {self.grade_level}"

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