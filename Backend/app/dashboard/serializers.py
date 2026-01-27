from rest_framework import serializers

from app.dashboard.models import (AiAssistantConfigModel, PlatformConfigModel,
                                  PrivacyAndPolicyModel,
                                  TermsAndConditionsModel)
from app.students.models import StudentActivity, VocabularySearch, StoryRecommendation
from app.story.models import StoryModel
from django.contrib.auth import get_user_model

User = get_user_model()


class RecentActivitySerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = StudentActivity
        fields = ['student_name', 'action_type', 'description', 'time_ago']

    def get_time_ago(self, obj):
        # You can use timesince here or a custom format
        from django.utils.timesince import timesince
        return timesince(obj.timestamp)

class AdminDashboardSerializer(serializers.Serializer):
    total_students = serializers.IntegerField()
    total_stories = serializers.IntegerField()
    recent_students_activity = RecentActivitySerializer(many=True)
    # We can also add a top vocabulary list here
    top_searched_words = serializers.SerializerMethodField()

    def get_top_searched_words(self, obj):
        top_words = VocabularySearch.objects.order_by('-search_count')[:5]
        return [{"word": w.word, "count": w.search_count} for w in top_words]
    
    
class AiAssistantConfigSerializer(serializers.ModelSerializer):
    behavior_instruction = serializers.SerializerMethodField()

    class Meta:
        model = AiAssistantConfigModel
        fields = ['assistant_name', 'ai_behaviour_settings', 'behavior_instruction']
        extra_kwargs = {
            'ai_behaviour_settings': {'read_only': True} # derived from behavior_instruction
        }

    def get_behavior_instruction(self, obj):
        # Return the main instruction from the JSON settings
        return obj.ai_behaviour_settings.get('instruction', '')

    def update(self, instance, validated_data):
        # Handle manual text update
        pass 
        # Actually, for the API View, we'll want to handle the specific text field input
        # But since we use partial=True in the view, we can override to_internal_value or just handle it in the view.
        # Let's add a write_only field for input.
        return super().update(instance, validated_data)

class AiAssistantConfigInputSerializer(serializers.ModelSerializer):
    behavior_instruction = serializers.CharField(write_only=True)
    
    class Meta:
        model = AiAssistantConfigModel
        fields = ['assistant_name', 'behavior_instruction']

    def update(self, instance, validated_data):
        if 'behavior_instruction' in validated_data:
            instruction = validated_data.pop('behavior_instruction')
            # detailed setting structure could be more complex, but for now:
            current_settings = instance.ai_behaviour_settings or {}
            current_settings['instruction'] = instruction
            instance.ai_behaviour_settings = current_settings
        
        return super().update(instance, validated_data)

class AdminStudentListSerializer(serializers.ModelSerializer):
    grade_level = serializers.IntegerField(source='student_profile.grade_level')
    vocabulary_proficiency = serializers.CharField(source='student_profile.vocabulary_proficiency')
    dictionary_search_count = serializers.SerializerMethodField()
    story_read_count = serializers.IntegerField(source='student_profile.total_books_read')
    reading_level = serializers.CharField(source='student_profile.vocabulary_proficiency') # redundant but requested

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'grade_level', 'vocabulary_proficiency', 
            'dictionary_search_count', 'story_read_count', 'reading_level',
            'is_active'
        ]

    def get_dictionary_search_count(self, obj):
        return StudentActivity.objects.filter(student=obj, action_type='VOCAB_SEARCH').count()

class StoryRecommendationSerializer(serializers.ModelSerializer):
    story_title = serializers.CharField(source='story.title', read_only=True)
    
    class Meta:
        model = StoryRecommendation
        fields = ['id', 'student', 'story', 'story_title', 'recommended_by', 'created_at']
        read_only_fields = ['recommended_by', 'created_at']
        
class PlatformConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformConfigModel
        fields = ['platform_name', 'contact_email', 'support_email']
        
class TermsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermsAndConditionsModel
        fields = ['content']

class PrivacySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivacyAndPolicyModel
        fields = ['content']