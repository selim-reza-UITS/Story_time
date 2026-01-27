from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from _config.services import send_welcome_email
from app.story.models import StoryModel
from app.students.models import StudentActivity, StudentProfile
from app.teachers.models import TeacherProfile
from app.students.serializers import StudentUserSerializer
from app.teachers.serializers import TeacherDashboardSerializer,TeacherSelfProfileSerializer

User = get_user_model()

class IsTeacherUser(permissions.BasePermission):
    """
    Allows access only to users with the is_teacher flag.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.is_teacher or request.user.is_admin_user))

class TeacherDashboardAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        

        if not user.is_teacher:
            return Response({"error": "Access denied. Teacher only."}, status=status.HTTP_403_FORBIDDEN)

        all_student_ids = User.objects.filter(is_student=True).values_list('id', flat=True)
        total_students = all_student_ids.count()

        total_stories = StoryModel.objects.filter(user_id__in=all_student_ids).count()

        vocab_activities = StudentActivity.objects.filter(
            student_id__in=all_student_ids, 
            action_type='VOCAB_SEARCH'
        )
        total_vocab_search = vocab_activities.count()
        
        avg_vocab = 0
        if total_students > 0:
            avg_vocab = round(total_vocab_search / total_students, 2)

        recent_activities = StudentActivity.objects.filter(
            student_id__in=all_student_ids
        ).select_related('student').order_by('-timestamp')[:10]

        dashboard_data = {
            "total_students": total_students,
            "total_stories": total_stories,
            "total_vocabulary_search": total_vocab_search,
            "average_vocabulary_searched": avg_vocab,
            "recent_student_activity": recent_activities
        }

        serializer = TeacherDashboardSerializer(dashboard_data)
        return Response(serializer.data)
    
class TeacherStudentListCreateAPIView(APIView):
    permission_classes = [IsTeacherUser]

    def get(self, request):
        # Teacher views ALL students
        students = User.objects.filter(is_student=True).select_related('student_profile')
        serializer = StudentUserSerializer(students, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def post(self, request):
        data = request.data
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return Response({"error": "Email and password are required."}, status=400)

        if User.objects.filter(email=email).exists():
            return Response({"error": "A student with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 1. Create User
        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            is_student=True
        )
        user.set_password(password)
        user.save()

        # 2. Create/Update Profile
        StudentProfile.objects.update_or_create(
            user=user,
            defaults={
                'grade_level': data.get('grade_level', 3),
                'vocabulary_proficiency': data.get('vocabulary_proficiency', 'beginner'),
                'assigned_teacher': request.user # Automatically assign to the teacher who created them
            }
        )

        # 3. Send Email
        try:
            send_welcome_email(user, password, "Student")
        except Exception as e:
            print(f"Email error: {e}")

        return Response({"message": "Student created successfully by teacher"}, status=status.HTTP_201_CREATED)


class TeacherStudentDetailAPIView(APIView):
    permission_classes = [IsTeacherUser]

    def get(self, request, pk):
        student = get_object_or_404(User, pk=pk, is_student=True)
        serializer = StudentUserSerializer(student)
        return Response(serializer.data)

    def put(self, request, pk):
        student = get_object_or_404(User, pk=pk, is_student=True)
        data = request.data
        
        # Update User fields
        student.first_name = data.get('first_name', student.first_name)
        student.last_name = data.get('last_name', student.last_name)
        student.email = data.get('email', student.email)
        student.save()

        # Update Profile fields
        profile = student.student_profile
        profile.grade_level = data.get('grade_level', profile.grade_level)
        profile.vocabulary_proficiency = data.get('vocabulary_proficiency', profile.vocabulary_proficiency)
        profile.save()

        return Response({"message": "Student profile updated successfully"})

    def delete(self, request, pk):
        student = get_object_or_404(User, pk=pk, is_student=True)
        student.delete()
        return Response({"message": "Student deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class TeacherStudentRecommendationAPIView(APIView):
    permission_classes = [IsTeacherUser]

    def post(self, request, pk):
        # Teacher recommends to a particular student (pk is student id)
        student = get_object_or_404(User, pk=pk, is_student=True)
        story_id = request.data.get('story_id')
        
        if not story_id:
            return Response({"error": "story_id is required"}, status=400)
            
        try:
            from app.students.models import StoryRecommendation
            rec, created = StoryRecommendation.objects.get_or_create(
                student=student, 
                story_id=story_id,
                defaults={'recommended_by': request.user}
            )
            return Response({"message": "Story recommended by teacher", "id": rec.id})
        except Exception as e:
            return Response({"error": str(e)}, status=400)
    


class TeacherMyProfileAPIView(APIView):
    """
    Get or Update the currently logged-in teacher's profile.
    """
    permission_classes = [IsTeacherUser]

    def get(self, request):
        if not request.user.is_teacher:
            return Response({"error": "Only teachers can access this profile."}, status=403)
        
        TeacherProfile.objects.get_or_create(user=request.user)
        
        serializer = TeacherSelfProfileSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        if not request.user.is_teacher:
            return Response({"error": "Only teachers can update this profile."}, status=403)

        serializer = TeacherSelfProfileSerializer(
            request.user, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Profile updated successfully",
                "data": serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        """
        Permanent account deletion for the teacher.
        """
        user = request.user

        if not user.is_teacher:
            return Response({"error": "Unauthorized."}, status=403)

        user.delete() 

        return Response(
            {"message": "Your account has been successfully deleted. We are sorry to see you go!"}, 
            status=status.HTTP_204_NO_CONTENT
        )
    
    