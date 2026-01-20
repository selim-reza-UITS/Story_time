from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class TeacherUserSerializer(serializers.ModelSerializer):
    grade_level = serializers.IntegerField(source='teacher_profile.grade_level')
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'grade_level', 'password']
        extra_kwargs = {'password': {'write_only': True}}