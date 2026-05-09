from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model 
from django.db import transaction
from accounts.models import *
import random
from django.core.cache import cache
from core.models import *
from course.models import *
from quiz.models import *
from accounts.models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                  'is_student', 'is_lecturer', 'is_parent', 'is_dep_head', 
                  'gender', 'phone', 'address', 'picture')


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    # Category-specific fields (Required depending on the role)
    level = serializers.CharField(required=False, allow_null=True)
    program = serializers.IntegerField(required=False, allow_null=True) # Program ID
    relation_ship = serializers.CharField(required=False, allow_null=True)
    student_id = serializers.IntegerField(required=False, allow_null=True) # For Parent registration

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name', 
                  'gender', 'phone', 'address', 'is_student', 'is_lecturer', 
                  'is_parent', 'is_dep_head', 'level', 'program', 
                  'relation_ship', 'student_id')

    @transaction.atomic
    def create(self, validated_data):
        # Extract profile specific data
        level = validated_data.pop('level', None)
        program_id = validated_data.pop('program', None)
        relation_ship = validated_data.pop('relation_ship', None)
        student_id = validated_data.pop('student_id', None)
        password = validated_data.pop('password')

        # Create base user
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        # Logic for Student Category
        if user.is_student:
            Student.objects.create(
                student=user,
                level=level,
                program_id=program_id
            )

        # Logic for Parent Category
        elif user.is_parent:
            Parent.objects.create(
                user=user,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                phone=user.phone,
                relation_ship=relation_ship,
                student_id=student_id
            )

        # Logic for Department Head Category
        elif user.is_dep_head:
            DepartmentHead.objects.create(
                user=user,
                department_id=program_id
            )

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value


class ResetPasswordConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        email = data.get('email')
        otp = data.get('otp')
        
        # Retrieve OTP from Redis
        cached_otp = cache.get(f"otp_{email}")
        
        if cached_otp is None:
            raise serializers.ValidationError("OTP expired or not found.")
        if cached_otp != otp:
            raise serializers.ValidationError("Invalid OTP.")
            
        return data
    
# user list
class StudentSerializer(serializers.ModelSerializer):
    # This includes the User details within the Student object
    student = UserSerializer(read_only=True)
    program_name = serializers.ReadOnlyField(source='program.title')

    class Meta:
        model = Student
        fields = ['id', 'student', 'level', 'program', 'program_name']

# Assign/Update a Student to a Program And/Or Level
class StudentProgramLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['program', 'level']

    def update(self, instance, validated_data):
        instance.program = validated_data.get('program', instance.program)
        instance.level = validated_data.get('level', instance.level)
        instance.save()
        return instance


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'


class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = ['id', 'semester', 'is_current_semester', 'next_semester_begins']

class SessionDetailSerializer(serializers.ModelSerializer):
    # This matches the reverse relationship from Session to Semester
    semesters = SemesterSerializer(many=True, read_only=True)

    class Meta:
        model = Session
        fields = ['id', 'session', 'is_current_session', 'next_session_begins', 'semesters']

# ActivityLog 
class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = ['id', 'message', 'created_at']


# News Serializers
class NewsAndEventsSerializer(serializers.ModelSerializer):
    # These fields are read-only because they are auto-generated by the model
    updated_date = serializers.DateTimeField(read_only=True)
    upload_time = serializers.DateTimeField(read_only=True)

    class Meta:
        model = NewsAndEvents
        fields = '__all__' 


#Session Serializers
class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ['id', 'session', 'is_current_session', 'next_session_begins'] 
    

# Programs & Courses 
class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = '__all__' 

# Courses
# class CourseSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Course
#         fields = '__all__' 


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'code', 'credit', 'summary', 'level', 'year', 'semester', 'is_elective', 'program', 'summary', 'year', 'credit']


# class CourseSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Course
#         fields = ['id', 'title', 'code', 'credit', 'semester', 'level']

class LecturerAllocationSerializer(serializers.ModelSerializer):
    # This nested serializer fetches the details of the courses from the M2M field
    courses = CourseSerializer(many=True, read_only=True)
    lecturer_name = serializers.ReadOnlyField(source='lecturer.get_full_name')
    email = serializers.ReadOnlyField(source='lecturer.email')

    class Meta:
        model = CourseAllocation
        fields = ['id', 'lecturer', 'lecturer_name', 'email', 'courses', 'session']


class ProgramDetailSerializer(serializers.ModelSerializer):
    # 'course_set' is the default related name Django uses 
    # since you didn't specify a related_name in the ForeignKey
    courses = CourseSerializer(source='course_set', many=True, read_only=True)

    class Meta:
        model = Program
        fields = ['id', 'title', 'summary', 'courses']


# Course Allocations
class CourseAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseAllocation
        fields = '__all__'

# Quizzes
class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = '__all__'
        read_only_fields = ('slug', 'timestamp')


class CourseAnnouncementSerializer(serializers.ModelSerializer):
    # User is read-only because we set it automatically from the request
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = CourseAnnouncement
        fields = ['id', 'course', 'user', 'content', 'timestamp']


class CourseDiscussionSerializer(serializers.ModelSerializer):
    sender_name = serializers.ReadOnlyField(source='sender.get_full_name')

    class Meta:
        model = CourseDiscussion
        fields = ['id', 'course', 'sender', 'sender_name', 'content', 'timestamp']
        read_only_fields = ['sender', 'timestamp']


class UploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Upload
        fields = ['id', 'title', 'file', 'updated_date']


class UploadVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadVideo
        fields = ['id', 'title', 'video', 'summary', 'timestamp']


# class CourseDetailSerializer(serializers.ModelSerializer):
#     # These names match the default 'related_name' (modelname_set)
#     files = UploadSerializer(source='upload_set', many=True, read_only=True)
#     videos = UploadVideoSerializer(source='uploadvideo_set', many=True, read_only=True)

#     class Meta:
#         model = Course
#         fields = [
#             'id', 'title', 'code', 'slug', 'credit', 
#             'summary', 'level', 'year', 'semester', 
#             'files', 'videos'
#         ]

User = get_user_model()

class LecturerSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField(source='get_full_name')

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'full_name', 'email']

class CourseDetailSerializer(serializers.ModelSerializer):
    # We use the related_name 'allocated_course' defined in the CourseAllocation model
    # to find all allocations associated with this course.
    assigned_lecturers = serializers.SerializerMethodField()
    files = UploadSerializer(source='upload_set', many=True, read_only=True)
    videos = UploadVideoSerializer(source='uploadvideo_set', many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'code', 'slug', 'credit', 'summary', 
            'level', 'year', 'semester', 'is_elective', 'files', 'videos', 'assigned_lecturers'
        ]

    def get_assigned_lecturers(self, obj):
        # Filter allocations that contain this course and extract the lecturer
        allocations = CourseAllocation.objects.filter(courses=obj)
        lecturers = [alloc.lecturer for alloc in allocations]
        return LecturerSerializer(lecturers, many=True).data

class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Upload
        fields = ['id', 'title', 'course', 'file', 'upload_time']

class VideoUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadVideo
        fields = ['id', 'title', 'course', 'video', 'summary', 'timestamp']