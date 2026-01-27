from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class StudentUserSerializer(serializers.ModelSerializer):
    grade_level = serializers.IntegerField(source='student_profile.grade_level')
    vocabulary_proficiency = serializers.CharField(source='student_profile.vocabulary_proficiency')
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'grade_level', 'vocabulary_proficiency', 'password']
        extra_kwargs = {'password': {'write_only': True}}


  
class StudentProfileSerializer(serializers.ModelSerializer):
    # Fields from StudentProfile model
    grade_level = serializers.IntegerField(source='student_profile.grade_level')
    vocabulary_proficiency = serializers.CharField(source='student_profile.vocabulary_proficiency')
    total_books_read = serializers.IntegerField(source='student_profile.total_books_read', read_only=True)
    words_learned = serializers.IntegerField(source='student_profile.words_learned', read_only=True)
    achievement_level = serializers.IntegerField(source='student_profile.achievement_level', read_only=True)
    level_title = serializers.CharField(source='student_profile.level_title', read_only=True)
    next_level_progress = serializers.FloatField(source='student_profile.next_level_progress', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'grade_level', 'vocabulary_proficiency', 
            'total_books_read', 'words_learned', 'is_student',
            'achievement_level', 'level_title', 'next_level_progress'
        ]
        # Email should typically be read-only for security, 
        # but username and names are editable.
        extra_kwargs = {
            'email': {'read_only': True},
            'id': {'read_only': True}
        }

    def update(self, instance, validated_data):
        # Extract profile data from the nested source
        profile_data = validated_data.pop('student_profile', {})
        
        # 1. Update User model fields
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()

        # 2. Update StudentProfile model fields
        profile = instance.student_profile
        profile.grade_level = profile_data.get('grade_level', profile.grade_level)
        profile.vocabulary_proficiency = profile_data.get('vocabulary_proficiency', profile.vocabulary_proficiency)
        profile.save()

        return instance