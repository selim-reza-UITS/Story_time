# app/story/views.py
import requests
from django.conf import settings
from rest_framework import generics, permissions,status
from .models import StoryModel, ReadingTrack
from .serializers import StoryLibrarySerializer, ContinueReadingSerializer, StoryCreateUpdateSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum
from django.utils.html import strip_tags
# --- API 1: All Story List (Filtered by Grade) ---
class StoryLibraryListView(generics.ListAPIView):
    serializer_class = StoryLibrarySerializer

    def get_queryset(self):
        user = self.request.user
        # Logic: Only show published books (not drafts) 
        # and match the student's grade level
        queryset = StoryModel.objects.filter(is_draft=False)
        
        if hasattr(user, 'student_profile'):
            grade = user.student_profile.grade_level
            queryset = queryset.filter(grade=grade)
            
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Regular Library
        library_serializer = self.get_serializer(queryset, many=True)
        
        # Recommendations
        recommendations = []
        if request.user.is_authenticated and hasattr(request.user, 'student_profile'):
             # Join with StoryRecommendation
             from app.students.models import StoryRecommendation
             recs = StoryRecommendation.objects.filter(student=request.user).select_related('story')
             # We want the story details
             rec_stories = [r.story for r in recs]
             recommendations = self.get_serializer(rec_stories, many=True).data
             
        return Response({
            "library": library_serializer.data,
            "recommended": recommendations
        })

# --- API 2: Story Reading Mode (Backend Pagination) ---
class StoryReadingView(APIView):
    """
    Handles Prev/Next logic by splitting story content into chunks.
    """
    def get(self, request, pk):
        story = get_object_or_404(StoryModel, pk=pk)
        
        # Get requested page from URL params (e.g., ?page=2), default to 1
        try:
            page_num = int(request.query_params.get('page', 1))
        except ValueError:
            page_num = 1

        # Define how many words per page (Adjust as needed for children)
        WORDS_PER_PAGE = 150 
        words = story.content.split()
        total_word_count = len(words)
        
        # Calculate total pages based on word count
        total_pages = (total_word_count // WORDS_PER_PAGE) + (1 if total_word_count % WORDS_PER_PAGE > 0 else 0)
        
        # Ensure page_num is within valid range
        page_num = max(1, min(page_num, total_pages))

        # Slice the words for the current page
        start_index = (page_num - 1) * WORDS_PER_PAGE
        end_index = start_index + WORDS_PER_PAGE
        page_content = " ".join(words[start_index:end_index])

        # Logic for Prev/Next buttons
        has_next = page_num < total_pages
        has_previous = page_num > 1

        # --- PROGRESS TRACKING LOGIC ---
        track, created = ReadingTrack.objects.get_or_create(
            student=request.user,
            story=story,
            defaults={'total_pages': total_pages}
        )
        track.current_page = page_num
        # Recalculate completion
        track.completion_percentage = (page_num / total_pages) * 100
        
        # Check completion
        if page_num == total_pages:
            if not track.is_completed:
                track.is_completed = True
                # Increment student profile stats
                # Increment student profile stats ONLY if user has a student profile
                if hasattr(request.user, 'student_profile'):
                    profile = request.user.student_profile
                    profile.total_books_read += 1
                    profile.save()
                    
                    # Log Activity
                    from app.students.models import StudentActivity
                    StudentActivity.objects.create(
                        student=request.user,
                        action_type='READ_COMPLETE',
                        description=f"Finished reading '{story.title}'"
                    )
        
        track.save()

        return Response({
            "id": story.id,
            "title": story.title,
            "page_content": page_content,
            "current_page": page_num,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_previous": has_previous,
            "words_remaining": max(0, total_word_count - end_index)
        }, status=status.HTTP_200_OK)
    
class MyStoryStatsListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_stories = StoryModel.objects.filter(user=request.user)
        total_stories_count = user_stories.count()
        total_pages_sum = user_stories.aggregate(Sum('total_pages'))['total_pages__sum'] or 0
        
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        edited_today_count = user_stories.filter(updated_at__gte=today_start).count()
        
        serializer = StoryLibrarySerializer(user_stories, many=True, context={'request': request})

        return Response({
            "total_Stories": total_stories_count,
            "total_page": total_pages_sum,
            "edited_totday": edited_today_count,
            "story_list": serializer.data
        }, status=status.HTTP_200_OK)
    
class StoryEditorAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    # 1. Fetch a specific story for the editor
    def get(self, request, pk):
        # hierarchical access: Teacher/Admin gets any story, Student gets only their own
        if request.user.is_teacher or request.user.is_admin_user or request.user.is_staff:
            story = get_object_or_404(StoryModel, pk=pk)
        else:
            story = get_object_or_404(StoryModel, pk=pk, user=request.user)
            
        serializer = StoryCreateUpdateSerializer(story, context={'request': request})
        return Response(serializer.data)

    # 2. Create a new story (Initial Save)
    def post(self, request):
        serializer = StoryCreateUpdateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            story = serializer.save()
            # Return full story details including absolute cover URL
            return Response({
                "id": story.id, 
                "message": "Story started!", 
                "story": StoryLibrarySerializer(story, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 3. Update story (Autosave / Publish / Image Upload)
    def patch(self, request, pk):
        if request.user.is_teacher or request.user.is_admin_user or request.user.is_staff:
            story = get_object_or_404(StoryModel, pk=pk)
        else:
            story = get_object_or_404(StoryModel, pk=pk, user=request.user)
            
        serializer = StoryCreateUpdateSerializer(story, data=request.data, partial=True, context={'request': request})
        
        if serializer.is_valid():
            story = serializer.save()
            return Response({
                "message": "Story saved successfully",
                "word_count": story.word_count,
                "total_pages": story.total_pages,
                "story": StoryLibrarySerializer(story, context={'request': request}).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 4. Delete story
    def delete(self, request, pk):
        if request.user.is_teacher or request.user.is_admin_user or request.user.is_staff:
            story = get_object_or_404(StoryModel, pk=pk)
        else:
            story = get_object_or_404(StoryModel, pk=pk, user=request.user)
            
        story.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class OwlbertChatAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        message = request.data.get('message')
        history = request.data.get('history', [])
        content_context = request.data.get('story_context', "")

        # FastAPI endpoint
        ai_base = getattr(settings, 'AI_SERVICE_URL', "http://localhost:8000")
        AI_URL = f"{ai_base}/chat" 

        import json
        # Safely get student profile - teachers/admins won't have one
        student_profile = getattr(request.user, 'student_profile', None)
        grade_level = student_profile.grade_level if student_profile else None
        
        payload = {
            "message": message,
            "conversation_history": history,
            "context": json.dumps({
                "student_name": request.user.username,
                "grade": grade_level,
                "current_writing": content_context
            })
        }

        try:
            # Forwarding to FastAPI Orchestrator
            print(f"Connecting to AI Service at: {AI_URL}") # Debug log
            response = requests.post(AI_URL, json=payload, timeout=30) # Increased timeout
            print(f"AI Service Response Code: {response.status_code}") # Debug log
            response.raise_for_status()
            ai_response = response.json()
            
            # Returns safe_response and speech_output (base64)
            return Response(ai_response, status=status.HTTP_200_OK)
        except Exception as e:
            import traceback
            traceback.print_exc() # Print full stack trace to console/logs
            print(f"Error connecting to AI service: {str(e)}")
            return Response({"chat_response": "I'm having trouble connecting to my owl-brain!", "speech_output": None, "debug_error": str(e)}, status=500)
        


class RealTimeCheckAPIView(APIView):
    """
    Fast endpoint for real-time spelling and grammar checking.
    Used during the 'Writing' process.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # 1. Get the current text chunk from the editor
        text_chunk = request.data.get('text', '')
        
        if not text_chunk or len(text_chunk) < 3:
            return Response({"suggestions": []})

        # 2. Clean HTML (AI works best on plain text)
        clean_text = strip_tags(text_chunk)

        # 3. Call FastAPI Grammar Service
        # Note: Using your AI developer's handle_grammar_request logic
        ai_base = getattr(settings, 'AI_SERVICE_URL', "http://localhost:8000")
        FASTAPI_URL = f"{ai_base}/grammar"
        
        try:
            response = requests.post(
                FASTAPI_URL, 
                json={"text": clean_text},
                timeout=30 # Increased timeout for reliability
            )
            
            if response.status_code == 200:
                corrected = response.json().get('corrected_text', '')
                
                # 4. Compare Original vs Corrected
                # If they are different, it means there was an error
                has_errors = clean_text.strip() != corrected.strip()

                return Response({
                    "original": clean_text,
                    "corrected": corrected,
                    "has_errors": has_errors,
                    "message": "Owlbert found some improvements!" if has_errors else "Looking good!"
                }, status=status.HTTP_200_OK)
            
            return Response({"error": "AI service busy"}, status=503)

        except requests.exceptions.Timeout:
            return Response({"error": "Timeout"}, status=408)

class DictionaryHelperAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        word = request.data.get('word', '').strip()
        action = request.data.get('action', 'lookup') # lookup or save
        
        if not word: return Response({"error": "Word required"}, status=400)
        
        from app.students.models import VocabularySearch, StudentSavedWord, StudentActivity

        # 1. Always track global search
        vocab, _ = VocabularySearch.objects.get_or_create(word=word.lower())
        vocab.search_count += 1
        vocab.last_searched = timezone.now()
        vocab.save()

        # 2. Log Activity
        StudentActivity.objects.create(
            student=request.user,
            action_type='VOCAB_SEARCH',
            description=f"Searched: {word}"
        )

        if action == 'save':
            saved, created = StudentSavedWord.objects.get_or_create(
                student=request.user, 
                word=word,
                defaults={'definition': vocab.definition} 
            )
            return Response({"message": "Word saved to your vocabulary list"})

        # Lookup logic
        # Check if we have definition, if not call AI
        definition = vocab.definition
        if not definition:
             # Call AI Learn Endpoint
             try:
                 ai_base = getattr(settings, 'AI_SERVICE_URL', "http://localhost:8000")
                 resp = requests.post(f"{ai_base}/learn", json={"word": word}, timeout=5)
                 if resp.status_code == 200:
                     data = resp.json()
                     definition = data.get('description', 'No definition found.')
                     # Update our DB
                     vocab.definition = definition
                     vocab.save()
             except:
                 definition = "Definition unavailable at the moment."

        return Response({
            "word": word,
            "definition": definition,
            "audio_url": request.build_absolute_uri(vocab.audio_spelling.url) if vocab.audio_spelling else None
        })

class ReadingTipsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Call AI for a random tip
        try:
             ai_base = getattr(settings, 'AI_SERVICE_URL', "http://localhost:8000")
             # Assuming AI has a /tips endpoint or use chat
             # For now, let's use a simple mock if AI doesn't support it, or call chat with prompt.
             # Ideally: requests.get(f"{ai_base}/tips")
             # Let's assume we use the chat endpoint for "Give me a reading tip"
             payload = {
                 "message": "Give me a short, fun reading tip for a grade 3 student.",
                 "conversation_history": []
             }
             resp = requests.post(f"{ai_base}/chat", json=payload, timeout=5)
             if resp.status_code == 200:
                 return Response({"tip": resp.json().get('safe_response')})
        except:
             pass
        
        # Fallback
        import random
        tips = [
            "Try to picture the story in your mind like a movie!",
            "If you don't know a word, click it to see what it means.",
            "Read out loud to practice your pronunciation.",
            "Ask yourself: 'What do I think will happen next?'"
        ]
        return Response({"tip": random.choice(tips)})
        

class ContinueReadingAPIView(APIView):
    """
    Returns stories that the student is currently reading (is_completed=False).
    Sorted by the most recently read.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # 1. Fetch reading tracks that are NOT completed
        active_tracks = ReadingTrack.objects.filter(
            student=request.user, 
            is_completed=False
        ).order_by('-last_read_at')

        # 2. If the user wants the "Primary" one (the big card in your image)
        # and then the rest as a list.
        serializer = ContinueReadingSerializer(active_tracks, many=True, context={'request': request})

        return Response({
            "count": active_tracks.count(),
            "reading_list": serializer.data
        }, status=status.HTTP_200_OK)

class StoryRatingAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        story_id = request.data.get('story_id')
        rating = request.data.get('rating')
        
        if not story_id or not rating:
            return Response({"error": "story_id and rating are required"}, status=400)
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                return Response({"error": "Rating must be between 1 and 5"}, status=400)
        except ValueError:
            return Response({"error": "Invalid rating"}, status=400)
        
        story = get_object_or_404(StoryModel, pk=story_id)
        # Simple average update (would need a separate Rating model for proper impl)
        # For now, just update the story rating
        story.rating = rating
        story.save()
        
        return Response({"message": "Rating submitted successfully", "new_rating": rating})

class StoryTrackAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        story_id = request.data.get('story_id')
        action = request.data.get('action')  # 'next' or 'finish'
        current_page = request.data.get('current_page', 1)
        
        if not story_id:
            return Response({"error": "story_id is required"}, status=400)
        
        story = get_object_or_404(StoryModel, pk=story_id)
        
        track, created = ReadingTrack.objects.get_or_create(
            student=request.user,
            story=story,
            defaults={'total_pages': story.total_pages}
        )
        
        if action == 'finish':
            track.current_page = story.total_pages
            track.completion_percentage = 100
            if not track.is_completed:
                track.is_completed = True
                # Increment profile stats
                profile = request.user.student_profile
                profile.total_books_read += 1
                profile.save()
            track.save()
            return Response({"message": "Story completed!", "completion": 100})
        else:
            # next action
            track.current_page = current_page
            track.completion_percentage = (current_page / story.total_pages) * 100
            track.save()
            return Response({
                "message": "Progress saved",
                "current_page": current_page,
                "completion": track.completion_percentage
            })