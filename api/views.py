from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import * 
from knox.models import AuthToken
import random
from django.core.mail import send_mail
from django.core.cache import cache 
from django.contrib.auth import get_user_model 
from .permissions import *
from core.models import NewsAndEvents
from course.models import *


class RegisterView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [] # Allow public registration

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "user": UserSerializer(user).data,
                "token": AuthToken.objects.create(user)[1]
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        # user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


class LogoutAPI(APIView):
    # Only authenticated users can access this endpoint
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            # Delete the token associated with the current user
            request._auth.delete()
            return Response(
                {"message": "Successfully logged out."}, 
                status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {"error": "Something went wrong or token already deleted."}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class UserAPI(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = str(random.randint(100000, 999999))
            
            # Store OTP in Redis for 10 minutes (600 seconds)
            cache.set(f"otp_{email}", otp, timeout=600)
            
            # Send Email
            send_mail(
                subject="Password Reset OTP",
                message=f"Your OTP for password reset is: {otp}. It expires in 10 minutes.",
                from_email="noreply@yourschool.com",
                recipient_list=[email],
                fail_silently=False,
            )
            
            return Response({"message": "OTP sent to your email."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordConfirmView(APIView):
    def post(self, request):
        serializer = ResetPasswordConfirmSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            new_password = serializer.validated_data['new_password']
            
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            
            # Delete OTP from Redis after successful reset
            cache.delete(f"otp_{email}")
            
            return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# Retrieve list of users - teachers & students 
User = get_user_model()

class StudentListView(generics.ListAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

class LecturerListView(generics.ListAPIView):
    queryset = User.objects.filter(is_lecturer=True)
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrLecturer]

# Change Student's Program/Level
class StudentProgramLevelUpdateView(generics.UpdateAPIView):
    """
    Endpoint to update a student's program and academic level.
    Only accessible by Admin/Superusers.
    """
    queryset = Student.objects.all()
    serializer_class = StudentProgramLevelSerializer
    permission_classes = [IsAdminOrLecturer]
    lookup_field = 'id'  # Use the Student profile ID or user ID depending on your URL structure


# ActivityLog Endpoint
class ActivityLogListView(generics.ListAPIView):
    """
    Endpoint to fetch all activity logs.
    Strictly accessible by Admin/Superusers.
    """
    queryset = ActivityLog.objects.all().order_by('-created_at')
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAdminOrLecturer]

# Create/Update/Delete must be for certain class of users 
# Teachers, Admin only. 
# Add to code.
class NewsAndEventsViewSet(viewsets.ModelViewSet):
    queryset = NewsAndEvents.objects.all().order_by('-upload_time')
    serializer_class = NewsAndEventsSerializer
    
    # Optional: Set permissions. 
    # Allow anyone to Read, but only authenticated users to Create/Update/Delete
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsAdminOrLecturer()]

# Programs & Courses Views
class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    # Apply the custom permission class [cite: 65]
    permission_classes = [IsSuperUserOrReadOnly] 


# Courses 
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsSuperUserOrReadOnly]
    lookup_field = 'slug'  # Uses slug instead of ID for detailed retrieval 

class CourseAllocationViewSet(viewsets.ModelViewSet):
    queryset = CourseAllocation.objects.all()
    serializer_class = CourseAllocationSerializer
    permission_classes = [IsSuperUserOrReadOnly]


# Quizzes Views
class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all().order_by('-timestamp')
    serializer_class = QuizSerializer
    permission_classes = [IsLecturerOrReadOnly]
    lookup_field = 'slug'

# CourseAnnouncements/ News
class CourseAnnouncementViewSet(viewsets.ModelViewSet):
    serializer_class = CourseAnnouncementSerializer
    permission_classes = [IsLecturerOrReadOnly]

    def perform_create(self, serializer):
        # Automatically set the current user as the announcement creator
        serializer.save(user=self.request.user)


class CourseDiscussionViewSet(viewsets.ModelViewSet):
    queryset = CourseDiscussion.objects.all().order_by('timestamp')
    serializer_class = CourseDiscussionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Automatically set the sender to the logged-in user
        serializer.save(sender=self.request.user)

