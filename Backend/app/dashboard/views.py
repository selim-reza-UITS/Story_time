from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from _config.services import send_welcome_email
from app.dashboard.models import (AiAssistantConfigModel, PlatformConfigModel,
                                  PrivacyAndPolicyModel,
                                  TermsAndConditionsModel)
from app.story.models import StoryModel
from app.students.models import (StudentActivity, StudentProfile,
                                 VocabularySearch)
from app.students.serializers import StudentUserSerializer
from app.teachers.models import TeacherProfile
from app.teachers.serializers import TeacherUserSerializer

from .serializers import (AdminDashboardSerializer,
                          AiAssistantConfigSerializer, AiAssistantConfigInputSerializer,
                          PlatformConfigSerializer, PrivacySerializer,
                          TermsSerializer, AdminStudentListSerializer, StoryRecommendationSerializer)

#
User = get_user_model()

class AdminDashboardView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        data = {
            "total_students": User.objects.filter(is_student=True).count(),
            "total_stories": StoryModel.objects.count(),
            "total_vocabulary_searched": VocabularySearch.objects.count(),
            "recent_students_activity": StudentActivity.objects.all()
        }
        
        serializer = AdminDashboardSerializer(data)
        return Response(serializer.data)

class VocabularySearchView(APIView):
    """
    Search for a word, track the search count, and return info + audio.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '').lower().strip()
        if not query:
            return Response({"error": "No word provided"}, status=400)

        # 1. Update or Create the search record
        vocab, created = VocabularySearch.objects.get_or_create(word=query)
        vocab.search_count += 1
        vocab.save()

        # 2. Log this as a student activity
        StudentActivity.objects.create(
            student=request.user,
            action_type='VOCAB_SEARCH',
            description=f"Searched for the word: '{query}'"
        )

        return Response({
            "word": vocab.word,
            "definition": vocab.definition or "Definition pending review",
            "audio_url": request.build_absolute_uri(vocab.audio_spelling.url) if vocab.audio_spelling else None,
            "search_count": vocab.search_count
        })
        
        
# --- STUDENT MANAGEMENT ---

class StudentListCreateAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        students = User.objects.filter(is_student=True).select_related('student_profile')
        serializer = AdminStudentListSerializer(students, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def post(self, request):
        data = request.data
        email = data.get('email')
        password = data.get('password')

        # 1. Check if user already exists to avoid another IntegrityError
        if User.objects.filter(email=email).exists():
            return Response({"error": "A user with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 2. Create User
        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            is_student=True
        )
        user.set_password(password)
        user.save()

        # 3. Use update_or_create instead of create
        # This safely handles signals and manual creation
        StudentProfile.objects.update_or_create(
            user=user,
            defaults={
                'grade_level': data.get('grade_level'),
                'vocabulary_proficiency': data.get('vocabulary_proficiency', 'beginner')
            }
        )

        # 4. Send Email
        try:
            send_welcome_email(user, password, "Student")
        except Exception as e:
            # Log the error but don't crash the request if email fails
            print(f"Email failed: {e}")

        return Response({"message": "Student added and email sent"}, status=status.HTTP_201_CREATED)

class StudentDetailAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, pk):
        student = get_object_or_404(User, pk=pk, is_student=True)
        # 1. Basic Info
        serializer = AdminStudentListSerializer(student)
        data = serializer.data
        
        # 2. Extra Stats as requested
        # total story read count:
        data['total_story_read_count'] = student.student_profile.total_books_read
        
        # total story created count:
        data['total_story_created_count'] = student.my_creative_stories.count() # assuming related_name='my_creative_stories' in StoryModel
        
        # all dictionary searched list:
        vocab_searches = VocabularySearch.objects.filter(word__in=student.activities.filter(action_type='VOCAB_SEARCH').values_list('description', flat=True)) 
        # Actually a better query would be:
        # But wait, VocabularySearch tracks global searches. StudentActivity tracks per student.
        # description="Searched for the word: '{query}'"
        # We need to parse or just list the activities.
        # Let's list the activities for now as that's what we have.
        # Or better, fetch StudentActivity of type VOCAB_SEARCH
        searches = student.activities.filter(action_type='VOCAB_SEARCH').values('description', 'timestamp')
        data['all_dictionary_searched_list'] = searches

        # recommended story list:
        recommendations = student.recommendations.select_related('story').all()
        data['recommended_story_list'] = StoryRecommendationSerializer(recommendations, many=True).data

        return Response(data)

    def put(self, request, pk):
        student = get_object_or_404(User, pk=pk, is_student=True)
        data = request.data
        
        student.first_name = data.get('first_name', student.first_name)
        student.last_name = data.get('last_name', student.last_name)
        student.email = data.get('email', student.email)
        student.save()

        profile = student.student_profile
        profile.grade_level = data.get('grade_level', profile.grade_level)
        profile.vocabulary_proficiency = data.get('vocabulary_proficiency', profile.vocabulary_proficiency)
        profile.save()

        return Response({"message": "Student updated successfully"})

    def delete(self, request, pk):
        student = get_object_or_404(User, pk=pk, is_student=True)
        student.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class StudentRecommendationAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        student = get_object_or_404(User, pk=pk, is_student=True)
        story_id = request.data.get('story_id')
        
        if not story_id:
            return Response({"error": "story_id is required"}, status=400)
            
        # Create recommendation
        try:
            from app.students.models import StoryRecommendation
            rec, created = StoryRecommendation.objects.get_or_create(
                student=student, 
                story_id=story_id,
                defaults={'recommended_by': request.user}
            )
            return Response({"message": "Story recommended", "id": rec.id})
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    def delete(self, request, pk):
        # Delete a specific recommendation by its ID (not student ID) - wait, the URL structure in views usually is /students/<id>/recommend/
        # But this view is likely mapped to /students/<pk>/recommend/
        # So pk is student_id.
        # To delete, we might need the story_id or the recommendation_id.
        # Let's assume we pass recommendation_id in body for now or use a different endpoint.
        # Given "action button : recommend story ... which will add to student's recommend list", POST is primary.
        # Un-recommend might be needed.
        pass


# --- TEACHER MANAGEMENT ---

class TeacherListCreateAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        teachers = User.objects.filter(is_teacher=True).select_related('teacher_profile')
        serializer = TeacherUserSerializer(teachers, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def post(self, request):
        data = request.data
        email = data.get('email')
        password = data.get('password')
        
        # 1. Create the User
        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            is_teacher=True
        )
        user.set_password(password)
        user.save()

        # 2. Use update_or_create to prevent IntegrityErrors
        TeacherProfile.objects.update_or_create(
            user=user,
            defaults={
                'grade_level': data.get('grade_level')
            }
        )

        send_welcome_email(user, password, "Teacher")
        return Response({"message": "Teacher added and email sent"}, status=status.HTTP_201_CREATED)

class TeacherDetailAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, pk):
        teacher = get_object_or_404(User, pk=pk, is_teacher=True)
        serializer = TeacherUserSerializer(teacher)
        return Response(serializer.data)

    def put(self, request, pk):
        teacher = get_object_or_404(User, pk=pk, is_teacher=True)
        data = request.data
        
        teacher.first_name = data.get('first_name', teacher.first_name)
        teacher.last_name = data.get('last_name', teacher.last_name)
        teacher.save()

        profile = teacher.teacher_profile
        profile.grade_level = data.get('grade_level', profile.grade_level)
        profile.save()

        return Response({"message": "Teacher updated successfully"})

    def delete(self, request, pk):
        teacher = get_object_or_404(User, pk=pk, is_teacher=True)
        teacher.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
class AiAssistantConfigAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        # Always get the first record, or create a default one if it doesn't exist
        config, _ = AiAssistantConfigModel.objects.get_or_create(id=1)
        serializer = AiAssistantConfigSerializer(config)
        return Response(serializer.data)

    def post(self, request):
        # We use id=1 to ensure we are always editing the same single record
        config, _ = AiAssistantConfigModel.objects.get_or_create(id=1)
        # Use IncomeSerializer for text input update
        serializer = AiAssistantConfigInputSerializer(config, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Return the full representation including the updated text
            return Response(AiAssistantConfigSerializer(config).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PlatformConfigAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        config, _ = PlatformConfigModel.objects.get_or_create(id=1)
        serializer = PlatformConfigSerializer(config)
        return Response(serializer.data)

    def post(self, request):
        config, _ = PlatformConfigModel.objects.get_or_create(id=1)
        serializer = PlatformConfigSerializer(config, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TermsAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET': return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def get(self, request):
        obj, _ = TermsAndConditionsModel.objects.get_or_create(id=1)
        serializer = TermsSerializer(obj)
        return Response(serializer.data)

    def post(self, request):
        obj, _ = TermsAndConditionsModel.objects.get_or_create(id=1)
        serializer = TermsSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PrivacyAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET': return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def get(self, request):
        obj, _ = PrivacyAndPolicyModel.objects.get_or_create(id=1)
        serializer = PrivacySerializer(obj)
        return Response(serializer.data)

    def post(self, request):
        obj, _ = PrivacyAndPolicyModel.objects.get_or_create(id=1)
        serializer = PrivacySerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)