from django.urls import path
from .views import RegisterAPI, LoginAPI, UserAPI

urlpatterns = [
    path('auth/register/', RegisterAPI.as_view(), name='api_register'),
    path('auth/login/', LoginAPI.as_view(), name='api_login'),
    path('auth/user/', UserAPI.as_view(), name='api_user_detail'),
]