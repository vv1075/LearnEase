from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from ..models import Course, Assignment, Submission, Grade, UserProfile


class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_professor = User.objects.create_user(username='professor', password='password')
        self.user_professor_profile = UserProfile.objects.create(user=self.user_professor, user_type='Professor')
        self.user_student = User.objects.create_user(username='student', password='password')
        self.user_student_profile = UserProfile.objects.create(user=self.user_student, user_type='Student')
        self.course = Course.objects.create(name='Test Course')
        self.assignment = Assignment.objects.create(
            title='Test Assignment',
            description='Test Description',
            course=self.course,
            created_by=self.user_professor,
            created_at=timezone.now(),
            due_date=timezone.now() + timezone.timedelta(days=7)
        )
        self.submission = Submission.objects.create(
            assignment=self.assignment,
            student=self.user_student,
            file='test_submission_file.txt',
            submitted_at=timezone.now()
        )
        self.grade = Grade.objects.create(
            assignment=self.assignment,
            student=self.user_student,
            score=90,
            graded_by=self.user_professor,
            graded_at=timezone.now()
        )

    def test_course_list_view(self):
        response = self.client.get(reverse('course_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/course_list.html')

    def test_create_assignment_view(self):
        self.client.force_login(self.user_professor)
        response = self.client.get(reverse('create_assignment', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/create_assignment.html')

    def test_submit_assignment_view(self):
        self.client.force_login(self.user_student)
        response = self.client.get(reverse('submit_assignment', args=[self.assignment.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/submit_assignment.html')

    def test_grade_submission_view(self):
        self.client.force_login(self.user_professor)
        response = self.client.get(reverse('grade_submission', args=[self.submission.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/grade_submission.html')

    # Add more test cases as needed...
