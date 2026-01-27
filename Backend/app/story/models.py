import re

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django_prose_editor.fields import ProseEditorField
from django.utils.html import strip_tags
class StoryModel(models.Model):
    # Link the story to the user (Can be Student or Admin)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='my_creative_stories'
    )
    
    # Core Story Fields
    title = models.CharField(max_length=255)
    # If blank, we will populate this in save() with the username
    author_name = models.CharField(max_length=255, default="Admin", null=True, blank=True)
    content = ProseEditorField()
    cover_image = models.ImageField(upload_to='story_covers/', null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.5)
    grade = models.IntegerField(default=3) 
    
    # Analytics Fields
    word_count = models.PositiveIntegerField(default=0)
    sentence_count = models.PositiveIntegerField(default=0)
    total_pages = models.PositiveIntegerField(default=1)
    
    # Status and Timestamps
    is_draft = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Stories"
        ordering = ['-created_at']

    def __str__(self):
        # FIX: Changed self.student.username to self.user.username
        return f"{self.title} by {self.user.username}"

    def save(self, *args, **kwargs):
        if self.content:
            # 1. Calculate Word Count
            plain_text = strip_tags(self.content)
            words = plain_text.split()
            self.word_count = len(words)

            # 2. Calculate Sentence Count
            sentences = re.split(r'[.!?]+', self.content)
            self.sentence_count = len([s for s in sentences if s.strip()])
            
            # 3. Calculate Total Pages (approx 1000 characters per page)
            char_count = len(self.content)
            self.total_pages = max(1, (char_count // 1000) + 1)

        # 4. Auto-populate author_name if it's a student writing their own story
        if not self.author_name or self.author_name == "Admin":
            if self.user.is_student:
                self.author_name = f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
        
        super(StoryModel, self).save(*args, **kwargs)



class ReadingTrack(models.Model):
    """
    Tracks a student's progress through a specific LibraryStory.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='reading_history'
    )
    story = models.ForeignKey(
        StoryModel, 
        on_delete=models.CASCADE, 
        related_name='tracks'
    )
    
    # Progress tracking
    # If the frontend displays by 'page', store page number. 
    # If it's a scroll, store percentage.
    current_page = models.PositiveIntegerField(default=1)
    total_pages = models.PositiveIntegerField(default=1)
    
    # Percentage 0.00 to 100.00
    completion_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    is_completed = models.BooleanField(default=False)
    
    # Meta
    last_read_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensures a student has only one track record per story
        unique_together = ('student', 'story')
        ordering = ['-last_read_at']

    def __str__(self):
        return f"{self.student.username} reading {self.story.title} ({self.completion_percentage}%)"

    def save(self, *args, **kwargs):
        # Auto-set is_completed if percentage is 100
        if self.completion_percentage >= 100:
            self.is_completed = True
        super().save(*args, **kwargs)
