from django.urls import path
from .views import *

urlpatterns = [
    # User Story
    path('auth/register/', RegisterAPI.as_view(), name='api_register'),
    path('auth/login/', LoginAPI.as_view(), name='api_login'),
    path('auth/logout/', LogoutAPI.as_view(), name='api_logout'),
    path('auth/user/', UserAPI.as_view(), name='api_user_detail'),
    path('auth/forgot-password/', ForgotPasswordView.as_view(), name='api_forgot_password'),
    path('auth/reset-password-confirm/', ResetPasswordConfirmView.as_view(), name='api_reset_password_confirm'),
    # News/Events Posting.
]