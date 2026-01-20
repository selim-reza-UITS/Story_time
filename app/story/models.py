import re
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class StoryModel(models.Model):
    # Link the story to the student (User model)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='my_creative_stories'
    )
    
    # Core Story Fields
    title = models.CharField(max_length=255)
    # TextField supports no limit and emojis (UTF-8)
    content = models.TextField() 
    cover_image = models.ImageField(upload_to='story_covers/', null=True, blank=True)
    
    # Analytics Fields (Calculated automatically)
    word_count = models.PositiveIntegerField(default=0)
    sentence_count = models.PositiveIntegerField(default=0)
    
    # Status and Timestamps
    is_draft = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Child Stories"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} by {self.student.username}"

    def save(self, *args, **kwargs):
        """
        Override save method to automatically update word and sentence counts
        before storing the data.
        """
        if self.content:
            # Calculate Word Count: Split by whitespace
            words = self.content.split()
            self.word_count = len(words)

            # Calculate Sentence Count: Look for periods, exclamation marks, or question marks
            # This regex handles emojis and standard punctuation
            sentences = re.split(r'[.!?]+', self.content)
            # Remove empty strings from the list
            self.sentence_count = len([s for s in sentences if s.strip()])
        
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
