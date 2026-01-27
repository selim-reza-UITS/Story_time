from django.contrib.auth import get_user_model
from django.db import models

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

    @property
    def achievement_level(self):
        # lvl 1 -> 5 story -> beginner
        read_count = self.total_books_read
        if read_count >= 30: return 5
        if read_count >= 20: return 4
        if read_count >= 15: return 3
        if read_count >= 10: return 2
        if read_count >= 5: return 1
        return 0

    @property
    def level_title(self):
        titles = {
            0: "Novice Reader",
            1: "Beginner Reader",
            2: "Word Explorer",
            3: "Story Adventurer",
            4: "Book Champion",
            5: "Reading Master"
        }
        return titles.get(self.achievement_level, "Novice Reader")

    @property
    def next_level_progress(self):
        # Calculate percentage to next level
        read_count = self.total_books_read
        if read_count >= 30: return 100
        
        thresholds = [0, 5, 10, 15, 20, 30]
        current_lvl = self.achievement_level
        if current_lvl >= 5: return 100
        
        next_threshold = thresholds[current_lvl + 1]
        prev_threshold = thresholds[current_lvl]
        
        # Simple percentage calculation: (current / target) * 100
        # Or progressive: (current - prev) / (next - prev) * 100
        # Let's do simple for now as per requirement "progres done to reach next level"
        # Requirement says "after reaching lvl 5 , it will show 100%"
        
        needed = next_threshold - prev_threshold
        done_in_level = read_count - prev_threshold
        return round((done_in_level / needed) * 100, 1)

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

class StoryRecommendation(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    story = models.ForeignKey('story.StoryModel', on_delete=models.CASCADE)
    recommended_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='recommended_stories')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'story')

    def __str__(self):
        return f"Story {self.story.title} recommended to {self.student.username}"

class StudentSavedWord(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_words')
    word = models.CharField(max_length=100)
    definition = models.TextField(blank=True)
    note = models.TextField(blank=True, null=True) # User's personal note
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'word')

    def __str__(self):
        return f"{self.student.username} saved {self.word}"