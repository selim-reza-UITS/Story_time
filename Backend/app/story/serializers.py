# app/story/serializers.py

from rest_framework import serializers
from .models import StoryModel,ReadingTrack

class StoryPageSerializer(serializers.ModelSerializer):
    """Serializer for a single page of the story"""
    page_content = serializers.SerializerMethodField()
    has_next = serializers.SerializerMethodField()
    has_previous = serializers.SerializerMethodField()

    class Meta:
        model = StoryModel
        fields = ['id', 'title', 'page_content', 'current_page', 'total_pages', 'has_next', 'has_previous']

    # Note: These fields are passed via 'context' from the view
    def get_page_content(self, obj):
        return self.context.get('page_content')

    def get_has_next(self, obj):
        return self.context.get('has_next')

    def get_has_previous(self, obj):
        return self.context.get('has_previous')

class StoryLibrarySerializer(serializers.ModelSerializer):
    """Serializer for the Story Library List Page"""
    story_id = serializers.IntegerField(source='id')
    story_title = serializers.CharField(source='title')
    
    class Meta:
        model = StoryModel
        fields = [
            'story_id', 
            'cover_image', 
            'story_title', 
            'author_name', 
            'rating', 
            'grade', 
            'total_pages'
        ]

class StoryDetailSerializer(serializers.ModelSerializer):
    """Serializer for the Reading/Details Page"""
    full_story = serializers.CharField(source='content')
    pagination_style = serializers.SerializerMethodField()

    class Meta:
        model = StoryModel
        fields = ['id', 'title', 'full_story', 'pagination_style', 'total_pages']

    def get_pagination_style(self, obj):
        # You can define styles like 'scroll' or 'flip' based on story length
        return "page-by-page"
    

class StoryCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoryModel
        fields = ['id', 'title', 'content', 'cover_image', 'is_draft', 'grade']
        extra_kwargs = {
            'user': {'read_only': True},
            'author_name': {'read_only': True}
        }

    def create(self, validated_data):
        # Assign the logged-in student as the user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    

class ContinueReadingSerializer(serializers.ModelSerializer):
    # Fetch details from the linked StoryModel
    story_id = serializers.ReadOnlyField(source='story.id')
    title = serializers.ReadOnlyField(source='story.title')
    cover_image = serializers.SerializerMethodField()
    
    class Meta:
        model = ReadingTrack
        fields = [
            'story_id', 
            'title', 
            'cover_image', 
            'current_page', 
            'total_pages', 
            'completion_percentage', 
            'last_read_at'
        ]

    def get_cover_image(self, obj):
        if obj.story.cover_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.story.cover_image.url)
            return obj.story.cover_image.url
        return None