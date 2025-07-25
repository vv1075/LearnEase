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

class SubmissionModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.course = Course.objects.create(name='Test Course')
        self.assignment = Assignment.objects.create(
            title='Test Assignment',
            description='Test Description',
            course=self.course,
            created_by=self.user,
            due_date=timezone.now()
        )
    
    def test_submission_creation(self):
        submission = Submission.objects.create(
            assignment=self.assignment,
            student=self.user,
            file='test_submission_file.txt',
            submitted_at=timezone.now()
        )
        self.assertEqual(submission.student, self.user)
        
class GradeModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.course = Course.objects.create(name='Test Course')
        self.assignment = Assignment.objects.create(
            title='Test Assignment',
            description='Test Description',
            course=self.course,
            created_by=self.user,
            due_date=timezone.now()
        )
    
    def test_grade_creation(self):
        grade = Grade.objects.create(
            assignment=self.assignment,
            student=self.user,
            score=90,
            graded_by=self.user,
            graded_at=timezone.now()
        )
        self.assertEqual(grade.score, 90)
                         