from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import * 
from knox.models import AuthToken
import random
from django.core.mail import send_mail
from django.core.cache import cache 
from django.contrib.auth import get_user_model 
from rest_framework.exceptions import PermissionDenied
from .permissions import *
from core.models import NewsAndEvents
from course.models import *

# Retrieve list of users - teachers & students 
User = get_user_model()

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


class ChangePasswordView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    # If you are calling this via PATCH, use the patch() method
    def patch(self, request, *args, **kwargs):
        # MANUALLY instantiate the serializer
        serializer = ChangeUserPasswordSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data.get("old_password")
            new_password = serializer.validated_data.get("new_password")

            if not user.check_password(old_password):
                return Response(
                    {"old_password": ["Wrong password."]}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            user.set_password(new_password)
            user.save()
            
            return Response(
                {'message': 'Password updated successfully'}, 
                status=status.HTTP_200_OK
            )
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    

class StudentListView(generics.ListAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]


class StudentDetailView(generics.RetrieveUpdateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]


class LecturerListView(generics.ListAPIView):
    queryset = User.objects.filter(is_lecturer=True)
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrLecturer]


class LecturerDetailsView(generics.RetrieveUpdateAPIView):
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


# Session management
class SessionListCreateView(generics.ListCreateAPIView):
    """
    Endpoint to list all sessions or create a new one.
    Strictly accessible by Admin/Superusers.
    """
    queryset = Session.objects.all().order_by('-id')
    serializer_class = SessionSerializer
    permission_classes = [IsSuperUserOrReadOnly]


class SessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [IsSuperUserOrReadOnly]
    lookup_field = 'id' 


class SessionDetailAPIView(generics.RetrieveAPIView):
    # Optimization: prefetch_related reduces database hits for the nested semesters
    queryset = Session.objects.prefetch_related('semesters').all()
    serializer_class = SessionDetailSerializer


class SemesterViewSet(viewsets.ModelViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    # Restrict access to Admin users only
    permission_classes = [IsSuperUserOrReadOnly] 


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


class ProgramDetailView(generics.RetrieveAPIView):
    queryset = Program.objects.all()
    serializer_class = ProgramDetailSerializer
    # lookup_field defaults to 'pk' (ID), which matches your requirement

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
# class CourseAnnouncementViewSet(viewsets.ModelViewSet):
#     serializer_class = CourseAnnouncementSerializer
#     permission_classes = [IsLecturerOrReadOnly]

#     def get_queryset(self):
#         # Returns all announcements ordered by newest first
#         return CourseAnnouncement.objects.all().order_by('-id')

#     def perform_create(self, serializer):
#         # Automatically set the current user as the announcement creator
#         serializer.save(user=self.request.user)

class CourseAnnouncementListCreateView(generics.ListCreateAPIView):
    serializer_class = CourseAnnouncementSerializer
    permission_classes = [IsLecturerOrReadOnly]

    def get_queryset(self):
        # Filters announcements strictly belonging to the course ID in the URL
        course_id = self.kwargs.get('course_id')
        return CourseAnnouncement.objects.filter(course_id=course_id).order_by('-timestamp')

    def perform_create(self, serializer):
        # Automatically attach the course from URL and current logged-in user
        course_id = self.kwargs.get('course_id')
        course = generics.get_object_or_404(Course, id=course_id)
        serializer.save(user=self.request.user, course=course)


class CourseAnnouncementDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CourseAnnouncementSerializer
    permission_classes = [IsLecturerOrReadOnly]
    lookup_field = 'id'

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        return CourseAnnouncement.objects.filter(course_id=course_id)


class CourseDiscussionViewSet(viewsets.ModelViewSet):
    queryset = CourseDiscussion.objects.all().order_by('timestamp')
    serializer_class = CourseDiscussionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Automatically set the sender to the logged-in user
        serializer.save(sender=self.request.user)


class CourseDetailAPIView(generics.RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseDetailSerializer
    # lookup_field defaults to 'pk' (ID), so no extra config needed


# class CourseFileUploadAPIView(generics.CreateAPIView):
#     queryset = Upload.objects.all()
#     serializer_class = FileUploadSerializer
#     permission_classes = [permissions.IsAuthenticated, IsAssignedLecturer]

#     def perform_create(self, serializer):
#         # Additional logic if you want to link the lecturer's ID to the upload
#         serializer.save()

class CourseFileUploadAPIView(generics.CreateAPIView, generics.DestroyAPIView):
    queryset = Upload.objects.all()
    serializer_class = FileUploadSerializer
    permission_classes = [permissions.IsAuthenticated, IsAssignedLecturer]

    def perform_create(self, serializer):
        # Additional logic if you want to link the lecturer's ID to the upload
        serializer.save()

    def perform_destroy(self, instance):
        # Optional: Delete the actual file from disk/storage before removing the database row
        if instance.file:  # Assuming your field name is 'file'
            instance.file.delete(save=False)
        instance.delete()



class CourseVideoUploadAPIView(generics.CreateAPIView, generics.DestroyAPIView):
    queryset = UploadVideo.objects.all()
    serializer_class = VideoUploadSerializer
    permission_classes = [permissions.IsAuthenticated, IsAssignedLecturer]

    def perform_create(self, serializer):
        # Additional logic if you want to link the lecturer's ID to the upload
        serializer.save()

    def perform_destroy(self, instance):
        # Optional: Delete the actual file from disk/storage before removing the database row
        if instance.file:  # Assuming your field name is 'file'
            instance.file.delete(save=False)
        instance.delete()

class LecturerCourseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows lecturer course allocations to be viewed.
    """
    queryset = CourseAllocation.objects.select_related('lecturer', 'session').prefetch_related('courses').all()
    serializer_class = LecturerAllocationSerializer

    # Optional: Filter by lecturer ID if passed in query params
    def get_queryset(self):
        queryset = super().get_queryset()
        lecturer_id = self.request.query_params.get('lecturer_id')
        if lecturer_id:
            queryset = queryset.filter(lecturer_id=lecturer_id)
        return queryset


class LecturerAssignedCoursesView(generics.ListAPIView):
    serializer_class = LecturerAssignedCoursesSerializer
    permission_classes = [IsLecturerUser]

    def get_queryset(self):
        # request.user is automatically derived from the authorization headers (Token/JWT/Session)
        user = self.request.user
        
        # Double-check safety constraints before querying allocations
        if not user.is_lecturer:
            raise PermissionDenied("Access restricted to lecturer accounts only.")
            
        # Filter CourseAllocation mapping by the logged-in lecturer
        return CourseAllocation.objects.filter(lecturer=user).select_related('session').prefetch_related('courses')


class StudentAssignedCoursesListView(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudentUser]

    def get_queryset(self):
        user = self.request.user
        
        try:
            # Access the student instance from the user model via one-to-one relationship
            student_profile = user.student
        except AttributeError:
            raise ValidationError({"detail": "No student profile found associated with this user account."})
        
        # Guard clause in case program or level is missing from student record
        if not student_profile.program or not student_profile.level:
            return Course.objects.none()

        # Fetch courses that match the student's current program and level
        return Course.objects.filter(
            program=student_profile.program,
            level=student_profile.level
        )