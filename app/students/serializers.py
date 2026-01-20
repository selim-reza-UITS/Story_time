from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()

class StudentUserSerializer(serializers.ModelSerializer):
    grade_level = serializers.IntegerField(source='student_profile.grade_level')
    vocabulary_proficiency = serializers.CharField(source='student_profile.vocabulary_proficiency')
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'grade_level', 'vocabulary_proficiency', 'password']
        extra_kwargs = {'password': {'write_only': True}}