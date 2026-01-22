from rest_framework import serializers
from app.students.models import StudentActivity,VocabularySearch
from app.dashboard.models import AiAssistantConfigModel,PlatformConfigModel,TermsAndConditionsModel,PrivacyAndPolicyModel

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
    class Meta:
        model = AiAssistantConfigModel
        fields = ['id', 'assistant_name', 'ai_behaviour_settings']
        
class PlatformConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformConfigModel
        fields = ['id', 'platform_name', 'contact_email', 'support_email']
        
class TermsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermsAndConditionsModel
        fields = ['id', 'content']

class PrivacySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivacyAndPolicyModel
        fields = ['id', 'content']