from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from app.story.models import StoryModel
from app.students.models import StudentActivity,VocabularySearch,StudentProfile
from app.teachers.models import TeacherProfile
from app.students.serializers import StudentUserSerializer
from app.teachers.serializers import TeacherUserSerializer
from app.dashboard.models import AiAssistantConfigModel,PlatformConfigModel,TermsAndConditionsModel,PrivacyAndPolicyModel
from .serializers import AdminDashboardSerializer,AiAssistantConfigSerializer,PlatformConfigSerializer,TermsSerializer,PrivacySerializer
from django.db import transaction
from _config.services import send_welcome_email
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
        serializer = StudentUserSerializer(students, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def post(self, request):
        data = request.data
        password = data.get('password')
        
        # 1. Create User
        user = User.objects.create_user(
            username=data.get('email'), # Using email as username
            email=data.get('email'),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            is_student=True
        )
        user.set_password(password)
        user.save()

        # 2. Create Profile
        StudentProfile.objects.create(
            user=user,
            grade_level=data.get('grade_level'),
            vocabulary_proficiency=data.get('vocabulary_proficiency', 'beginner')
        )

        # 3. Send Email
        send_welcome_email(user, password, "Student")

        return Response({"message": "Student added and email sent"}, status=status.HTTP_201_CREATED)

class StudentDetailAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, pk):
        student = get_object_or_404(User, pk=pk, is_student=True)
        serializer = StudentUserSerializer(student)
        return Response(serializer.data)

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
        password = data.get('password')
        
        user = User.objects.create_user(
            username=data.get('email'),
            email=data.get('email'),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            is_teacher=True
        )
        user.set_password(password)
        user.save()

        TeacherProfile.objects.create(
            user=user,
            grade_level=data.get('grade_level')
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
    """
    Handle List, Create, and Patch for AI configurations.
    Patch uses query params: ?id=X
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        configs = AiAssistantConfigModel.objects.all()
        serializer = AiAssistantConfigSerializer(configs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AiAssistantConfigSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        # 1. Get ID from query parameters (?id=1)
        config_id = request.query_params.get('id')
        
        if not config_id:
            return Response(
                {"error": "Please provide an 'id' in the query parameters. Example: ?id=1"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Find the object
        config = get_object_or_404(AiAssistantConfigModel, pk=config_id)
        
        # 3. Partially update
        serializer = AiAssistantConfigSerializer(config, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "AI Assistant settings updated successfully",
                "data": serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class PlatformConfigAPIView(APIView):
    """
    Manage Platform Configurations (Name, Contact Email, Support Email).
    PATCH/DELETE operations use query params: ?id=X
    Access: Admin Only
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        configs = PlatformConfigModel.objects.all()
        serializer = PlatformConfigSerializer(configs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PlatformConfigSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        # Extract ID from query params (?id=1)
        config_id = request.query_params.get('id')
        
        if not config_id:
            return Response(
                {"error": "Please provide an 'id' in the query parameters. Example: ?id=1"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        config = get_object_or_404(PlatformConfigModel, pk=config_id)
        
        # Partially update the model
        serializer = PlatformConfigSerializer(config, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Platform configuration updated successfully",
                "data": serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class TermsAPIView(APIView):
    """
    Manage Terms and Conditions.
    GET: Public | POST/PATCH: Admin Only
    PATCH uses query params: ?id=X
    """
    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def get(self, request):
        content = TermsAndConditionsModel.objects.all()
        serializer = TermsSerializer(content, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TermsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        obj_id = request.query_params.get('id')
        if not obj_id:
            return Response({"error": "ID required in query params (?id=X)"}, status=400)
        
        obj = get_object_or_404(TermsAndConditionsModel, pk=obj_id)
        serializer = TermsSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PrivacyAPIView(APIView):
    """
    Manage Privacy Policy.
    GET: Public | POST/PATCH: Admin Only
    PATCH uses query params: ?id=X
    """
    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def get(self, request):
        content = PrivacyAndPolicyModel.objects.all()
        serializer = PrivacySerializer(content, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PrivacySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        obj_id = request.query_params.get('id')
        if not obj_id:
            return Response({"error": "ID required in query params (?id=X)"}, status=400)
        
        obj = get_object_or_404(PrivacyAndPolicyModel, pk=obj_id)
        serializer = PrivacySerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)