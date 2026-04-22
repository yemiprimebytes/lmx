from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from course.models import *
from accounts.models import *
from quiz.models import *
import logging

User = get_user_model()
logger = logging.getLogger('lmx')

class LMSTests(APITestCase):

    def setUp(self):
        # Initial Setup for metadata
        self.program = Program.objects.create(title="Computer Science")
        self.course = Course.objects.create(
            title="Intro to Python", 
            code="CS101", 
            program=self.program,
            slug="intro-to-python"
        )
        
        # User Categories
        self.superuser = User.objects.create_superuser(
            username='admin', password='password123', email='admin@test.com'
        )
        self.lecturer = User.objects.create_user(
            username='lecturer1', password='password123', is_lecturer=True
        )
        self.student_user = User.objects.create_user(
            username='student1', password='password123', is_student=True
        )
        self.student_profile = Student.objects.create(
            student=self.student_user, level="Bachelor", program=self.program
        )

    def _log_if_error(self, response, expected_status, test_name):
        """Helper to log details if the response status is unexpected."""
        if response.status_code != expected_status:
            logger.error(f"Test '{test_name}' failed. Expected {expected_status}, got {response.status_code}. Data: {response.data}")

    # 1. AUTHENTICATION & REGISTRATION TESTS
    def test_student_registration(self):
        url = reverse('api_register')
        data = {
            "username": "new_student",
            "password": "password123",
            "email": "new@student.com",
            "is_student": True,
            "level": "Bachelor",
            "program": self.program.id
        }
        response = self.client.post(url, data)
        self._log_if_error(response, status.HTTP_201_CREATED, "test_student_registration")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Student.objects.filter(student__username="new_student").exists())

    def test_login(self):
        url = reverse('api_login')
        data = {"username": self.student_user.username, "password": "password123"}
        response = self.client.post(url, data)
        self._log_if_error(response, status.HTTP_200_OK, "test_login")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    # 2. COURSE PERMISSIONS (Superuser Only)
    def test_create_course_restricted_to_superuser(self):
        url = reverse('courses-list')
        data = {"title": "Advanced Java", "code": "CS202", "program": self.program.id}
        
        # Student attempts to create
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(url, data)
        self._log_if_error(response, status.HTTP_403_FORBIDDEN, "test_create_course_student")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Admin attempts to create
        self.client.force_authenticate(user=self.superuser)
        response = self.client.post(url, data)
        self._log_if_error(response, status.HTTP_201_CREATED, "test_create_course_admin")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # 3. QUIZ & ANNOUNCEMENT PERMISSIONS (Lecturer Only)
    def test_lecturer_can_create_announcement(self):
        url = reverse('course-announcements-list')
        data = {"course": self.course.id, "content": "Welcome to class!"}
        
        self.client.force_authenticate(user=self.lecturer)
        response = self.client.post(url, data)
        self._log_if_error(response, status.HTTP_201_CREATED, "test_lecturer_can_create_announcement")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user'], self.lecturer.id)

    def test_student_cannot_create_quiz(self):
        url = reverse('quizzes-list')
        data = {"title": "Quiz 1", "course": self.course.id}
        
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(url, data)
        self._log_if_error(response, status.HTTP_403_FORBIDDEN, "test_student_cannot_create_quiz")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # 4. DISCUSSION PERMISSIONS (Participant Read/Write, Owner-Only Edit)
    def test_discussion_ownership(self):
        # Lecturer creates a comment
        discussion = CourseDiscussion.objects.create(
            course=self.course, sender=self.lecturer, content="Hello Students"
        )
        url = reverse('course-discussions-detail', kwargs={'pk': discussion.pk})
        
        # Student attempts to EDIT lecturer's comment
        self.client.force_authenticate(user=self.student_user)
        response = self.client.patch(url, {"content": "Hacked content"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Lecturer edits their own comment
        self.client.force_authenticate(user=self.lecturer)
        response = self.client.patch(url, {"content": "Hello everyone!"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # 5. GENERAL VIEWING (Read-Only access)
    def test_student_can_view_quizzes(self):
        Quiz.objects.create(title="Midterm", course=self.course)
        url = reverse('quizzes-list')
        
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)