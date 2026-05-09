from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

# Create a router and register our viewset with it.
router = DefaultRouter()
router.register(r'news-events', NewsAndEventsViewSet, basename='news-events')
router.register(r'programs', ProgramViewSet, basename='programs')
router.register(r'courses', CourseViewSet, basename='courses')
router.register(r'course-allocations', CourseAllocationViewSet, basename='course-allocations')
router.register(r'quizzes', QuizViewSet, basename='quizzes')
router.register(r'course-announcements', CourseAnnouncementViewSet, basename='course-announcements')
router.register(r'discussions', CourseDiscussionViewSet, basename='course-discussions')
router.register(r'semesters', SemesterViewSet)
router.register(r'lecturer-courses', LecturerCourseViewSet, basename='lecturer-courses')

urlpatterns = [
    # User Story
    path('auth/register/', RegisterView.as_view(), name='api_register'),
    path('auth/login/', LoginAPI.as_view(), name='api_login'),
    path('auth/logout/', LogoutAPI.as_view(), name='api_logout'),
    path('auth/user/', UserAPI.as_view(), name='api_user_detail'),
    path('auth/forgot-password/', ForgotPasswordView.as_view(), name='api_forgot_password'),
    path('auth/reset-password-confirm/', ResetPasswordConfirmView.as_view(), name='api_reset_password_confirm'),
    # News/Events Posting.
    path('', include(router.urls)),
    path('accounts/students/', StudentListView.as_view(), name='student-list'),
    path('accounts/lecturers/', LecturerListView.as_view(), name='lecturer-list'),
    path('accounts/students/<int:pk>/', StudentDetailView.as_view(), name='student-detail'),
    path('accounts/students/<int:id>/update-academic-info/', StudentProgramLevelUpdateView.as_view(), name='update-student-academic'),
    path('activity-logs/', ActivityLogListView.as_view(), name='activity-log-list'),
    #session  & Sementer URLs
    path('sessions/', SessionListCreateView.as_view(), name='session-list-create'),
    path('sessions/<int:id>/', SessionDetailView.as_view(), name='session-detail'),
    path('program-details/<int:pk>/', ProgramDetailView.as_view(), name='program-details'),
    path('course-details/<int:pk>/', CourseDetailAPIView.as_view(), name='course-details'),
    path('session-details/<int:pk>/', SessionDetailAPIView.as_view(), name='session-detail'),
    path('upload/file/', CourseFileUploadAPIView.as_view(), name='api-file-upload'),
    path('upload/video/', CourseVideoUploadAPIView.as_view(), name='api-video-upload'),
]
