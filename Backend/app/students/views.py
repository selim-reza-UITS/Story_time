from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .serializers import StudentProfileSerializer

class StudentProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: View Profile
    PUT/PATCH: Edit Profile
    DELETE: Delete Account
    """
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Always return the profile of the currently logged-in user
        return self.request.user

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return Response(
            {"message": "Account deleted successfully."}, 
            status=status.HTTP_204_NO_CONTENT
        )

class StudentHomeAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user
        profile = getattr(user, 'student_profile', None)
        
        if not profile:
             return Response({"error": "Student profile not found"}, status=404)
             
        # 1. Unfinished Stories (Continue Reading)
        # Using ReadingTrack model
        from app.story.models import ReadingTrack
        from app.story.serializers import ContinueReadingSerializer
        unfinished_tracks = ReadingTrack.objects.filter(student=user, is_completed=False).order_by('-last_read_at')
        unfinished_data = ContinueReadingSerializer(unfinished_tracks, many=True).data
        
        # 2. Finished Books
        finished_tracks = ReadingTrack.objects.filter(student=user, is_completed=True).order_by('-last_read_at')
        finished_data = ContinueReadingSerializer(finished_tracks, many=True).data

        # 3. Vocabulary
        from app.students.models import StudentSavedWord
        saved_words = StudentSavedWord.objects.filter(student=user).order_by('-saved_at')
        vocab_list = {w.word: w.definition for w in saved_words}
        
        # 4. Stats
        stats = {
            "total_book_read": profile.total_books_read,
            "total_new_words_learned": saved_words.count(), # or profile.words_learned if updated separately
            "reading_level": profile.vocabulary_proficiency, # or calculated
            "reading_title": profile.level_title,
            "next_level_progress": profile.next_level_progress
        }

        return Response({
            "unfinished_story_list": unfinished_data,
            "finished_story_list": finished_data,
            "vocabulary_list": vocab_list,
            "stats": stats
        })

class StudentVocabularyListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        from app.students.models import StudentSavedWord
        saved_words = StudentSavedWord.objects.filter(student=request.user).order_by('-saved_at')
        data = [{"word": w.word, "definition": w.definition, "saved_at": w.saved_at} for w in saved_words]
        return Response({"count": saved_words.count(), "words": data})

class StudentAchievementAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user
        profile = getattr(user, 'student_profile', None)
        
        if not profile:
            return Response({"error": "Profile not found"}, status=404)
        
        # Get daily streak (simplified - would need a login tracking model for full impl)
        daily_streak = 1  # Placeholder
        
        return Response({
            "username": user.get_full_name() or user.username,
            "current_reading_level": profile.achievement_level,
            "reading_level_name": profile.level_title,
            "next_level_progress": profile.next_level_progress,
            "books_read_total": profile.total_books_read,
            "words_discovered_total": user.saved_words.count() if hasattr(user, 'saved_words') else 0,
            "daily_streak": daily_streak
        })

class StudentLogoutAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        # Track logout for streak purposes (would need actual implementation)
        # For now, just acknowledge
        return Response({"message": "Logged out successfully. Keep reading!"})