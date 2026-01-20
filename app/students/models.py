from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
# Create your models here.

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


class StudentActivity(models.Model):
    ACTION_CHOICES = [
        ('STORY_CREATE', 'Created a Story'),
        ('STORY_UPDATE', 'Updated a Story'),
        ('READ_START', 'Started Reading'),
        ('READ_COMPLETE', 'Finished Reading'),
        ('VOCAB_SEARCH', 'Searched Vocabulary'),
    ]

    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='activities'
    )
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.CharField(max_length=255) # e.g., "Read 'The Magic Tree'"
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "Student Activities"

    def __str__(self):
        return f"{self.student.username} - {self.action_type}"
    
class VocabularySearch(models.Model):
    word = models.CharField(max_length=100, unique=True)
    audio_spelling = models.FileField(upload_to='vocab_audio/', null=True, blank=True)
    definition = models.TextField(blank=True)
    search_count = models.PositiveIntegerField(default=0)
    last_searched = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.word