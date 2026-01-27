from django.urls import include, path

from app.accounts import views as accounts
from app.dashboard import views as admin
from app.teachers import views as teachers
from app.story import views as story
from app.students import views as students


STORY_PATTERN = [
    path('library/', story.StoryLibraryListView.as_view(), name='story-list'),
    path('read/<int:pk>/', story.StoryReadingView.as_view(), name='story-reading'),
    path('editor/', story.StoryEditorAPIView.as_view(), name='editor-create'),
    path('editor/<int:pk>/', story.StoryEditorAPIView.as_view(), name='editor-detail'),
    path('chat/owlbert/', story.OwlbertChatAPIView.as_view(), name='owlbert-chat'),
    path('ai/realtime-check/', story.RealTimeCheckAPIView.as_view(), name='realtime-check'),
    path('continue-reading/', story.ContinueReadingAPIView.as_view(), name='continue-reading'),
    path('dictionary/', story.DictionaryHelperAPIView.as_view(), name='dictionary-helper'),
    path('tips/', story.ReadingTipsAPIView.as_view(), name='reading-tips'),
    path('rate/', story.StoryRatingAPIView.as_view(), name='story-rate'),
    path('track/', story.StoryTrackAPIView.as_view(), name='story-track'),
]


STUDENT_PATTERN = [
    path('forgot-password/', accounts.ForgotPasswordView.as_view(), name='forgot-password'),
    path('verify-otp/', accounts.VerifyOTPView.as_view(), name='verify-otp'),
    path('verify-otp/', accounts.VerifyOTPView.as_view(), name='verify-otp'),
    path('reset-password/', accounts.ResetPasswordView.as_view(), name='reset-password'),
    path('home/', students.StudentHomeAPIView.as_view(), name='student-home'),
    #
    path('get/terms-and-conditions/',admin.TermsAPIView.as_view(),name="Term-and-conditions"),
    path('get/privacy-and-policy/',admin.PrivacyAPIView.as_view(),name="privacy-policy"),
    #
    path('my-stories/stats/', story.MyStoryStatsListView.as_view(), name='my-stories-stats'),
    #
    path('profile/', students.StudentProfileDetailView.as_view(), name='student-profile'),
    path('vocabulary/', students.StudentVocabularyListAPIView.as_view(), name='student-vocabulary'),
    path('achievements/', students.StudentAchievementAPIView.as_view(), name='student-achievements'),
    path('logout/', students.StudentLogoutAPIView.as_view(), name='student-logout'),

]


ADMIN_PATTERN = [
    path("overview/",admin.AdminDashboardView.as_view(),name="adminOverview"),
    #
    path('admin/students/', admin.StudentListCreateAPIView.as_view(), name='student-list-create'),
    path('admin/students/<int:pk>/', admin.StudentDetailAPIView.as_view(), name='student-detail'),
    path('admin/students/<int:pk>/recommend/', admin.StudentRecommendationAPIView.as_view(), name='student-recommend'),
    #
    path('admin/teachers/', admin.TeacherListCreateAPIView.as_view(), name='teacher-list-create'),
    path('admin/teachers/<int:pk>/', admin.TeacherDetailAPIView.as_view(), name='teacher-detail'),
    #
    path('config/ai/behavior/',admin.AiAssistantConfigAPIView.as_view(),name="ai-behaviour"),
    path('config/platform/',admin.PlatformConfigAPIView.as_view(),name="Platform Settings"),
    path('config/terms-and-conditions/',admin.TermsAPIView.as_view(),name="Term-and-conditions"),
    path('config/privacy-and-policy/',admin.PrivacyAPIView.as_view(),name="privacy-policy")
]


TEACHER_PATTERN = [
    path("dashboard/",teachers.TeacherDashboardAPIView.as_view(),name="teacher-dashboard"),
    #
    path('all/students/', teachers.TeacherStudentListCreateAPIView.as_view(), name='teacher-student-list'),
    path('students/<int:pk>/action/', teachers.TeacherStudentDetailAPIView.as_view(), name='teacher-student-detail'),
    path('students/<int:pk>/recommend/', teachers.TeacherStudentRecommendationAPIView.as_view(), name='teacher-recommend'),
    #
    path('my-profile/', teachers.TeacherMyProfileAPIView.as_view(), name='teacher-self-profile'),
    #
    path('get/terms-and-conditions/',admin.TermsAPIView.as_view(),name="Term-and-conditions"),
    path('get/privacy-and-policy/',admin.PrivacyAPIView.as_view(),name="privacy-policy")
]

urlpatterns = [
    path("auth/login/", accounts.LoginAPIView.as_view(), name="login"),
    path("site/",include(ADMIN_PATTERN)),
    path("teachers/",include(TEACHER_PATTERN)),
    path("students/",include(STUDENT_PATTERN)),
    path("stories/",include(STORY_PATTERN)),
]
