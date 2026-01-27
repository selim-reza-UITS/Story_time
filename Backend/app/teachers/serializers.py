from django.contrib.auth import get_user_model
from django.utils.timesince import timesince
from rest_framework import serializers

from app.students.models import StudentActivity

User = get_user_model()


class TeacherUserSerializer(serializers.ModelSerializer):
    grade_level = serializers.IntegerField(source='teacher_profile.grade_level')
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'grade_level', 'password']
        extra_kwargs = {'password': {'write_only': True}}

class TeacherStudentActivitySerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_username = serializers.CharField(source='student.username', read_only=True)
    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = StudentActivity
        fields = ['student_name', 'student_username', 'action_type', 'description', 'time_ago', 'timestamp']

    def get_time_ago(self, obj):
        return timesince(obj.timestamp) + " ago"

class TeacherDashboardSerializer(serializers.Serializer):
    total_students = serializers.IntegerField()
    total_stories = serializers.IntegerField()
    total_vocabulary_search = serializers.IntegerField()
    average_vocabulary_searched = serializers.FloatField()
    recent_student_activity = TeacherStudentActivitySerializer(many=True)

class TeacherSelfProfileSerializer(serializers.ModelSerializer):
    grade_level = serializers.IntegerField(source='teacher_profile.grade_level')
    bio = serializers.CharField(source='teacher_profile.bio', allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'grade_level', 'bio']
        read_only_fields = ['id', 'username', 'email']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('teacher_profile', {})
        
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()

        profile = instance.teacher_profile
        profile.grade_level = profile_data.get('grade_level', profile.grade_level)
        profile.bio = profile_data.get('bio', profile.bio)
        profile.save()

        return instance
  

