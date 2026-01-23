from django.urls import path,include
from app.dashboard import views as admin
from app.accounts import views as accounts

ADMIN_PATTERN = [
    path("overview/",admin.AdminDashboardView.as_view(),name="adminOverview"),
    #
    path('admin/students/', admin.StudentListCreateAPIView.as_view(), name='student-list-create'),
    path('admin/students/<int:pk>/', admin.StudentDetailAPIView.as_view(), name='student-detail'),
    #
    path('admin/teachers/', admin.TeacherListCreateAPIView.as_view(), name='teacher-list-create'),
    path('admin/teachers/<int:pk>/', admin.TeacherDetailAPIView.as_view(), name='teacher-detail'),
    #
    path('config/ai/behavior/',admin.AiAssistantConfigAPIView.as_view(),name="ai-behaviour"),
    path('config/platform/',admin.PlatformConfigAPIView.as_view(),name="Platform Settings"),
    path('config/terms-and-conditions/',admin.TermsAPIView.as_view(),name="Term-and-conditions"),
    path('config/privacy-and-policy/',admin.PrivacyAPIView.as_view(),name="privacy-policy")
]

urlpatterns = [
    path("auth/login/", accounts.LoginAPIView.as_view(), name="login"),
    path("site/",include(ADMIN_PATTERN)),
]
