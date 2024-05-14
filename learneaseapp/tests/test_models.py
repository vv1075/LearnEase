from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from ..models import Course, Assignment, Submission, Grade

class CourseModelTestCase(TestCase):
    def test_course_creation(self):
        course = Course.objects.create(name='Test Course')
        self.assertEqual(course.name, 'Test Course')
        
class AssignmentModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.course = Course.objects.create(name='Test Course')
    
    def test_assignment_creation(self):
        assignment = Assignment.objects.create(
            title='Test Assignment',
            description='Test Description',
            course=self.course,
            created_by=self.user,
            due_date=timezone.now()
        )
        self.assertEqual(assignment.title, 'Test Assignment')