from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('Professor', 'Professor'),
        ('Student', 'Student'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, blank=True)
    


    def __str__(self):
        return self.user.username
    
class SavedBook(models.Model):

    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    count = models.IntegerField(blank=True, null=True)
    categories = models.CharField(max_length=255, blank=True, null=True)
    rating = models.FloatField(blank=True, null=True)
    thumbnail = models.URLField(blank=True, null=True)
    preview = models.URLField(blank=True, null=True)
                              
class Course(models.Model):
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    # Add other fields as needed

    def __str__(self):
        return self.name

class Assignment(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField()

    def __str__(self):
        return self.title 
    
class QuizAssignment(models.Model):
    quiz_id = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    assigned_students = models.ManyToManyField(User)

    def __str__(self):
        return f"Quiz {self.quiz_id} for {self.course.name}"
    
    
class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(default=timezone.now)

    def _str_(self):
        return f"{self.assignment.title} - {self.student.username}"    
    
class Grade(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    graded_by = models.ForeignKey(User, related_name='grader', on_delete=models.CASCADE)
    graded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.assignment.title} - {self.student.username}"

class Notess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    description= models.TextField()
    
    def __str__(self):
        return str(self.title)
    
    class Meta:
        verbose_name = "notes"
        verbose_name_plural = "notes"
    
class QuizSubmissionStatus(models.Model):
    quiz_id = models.CharField(max_length=100)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    submitted = models.BooleanField(default=False)
    retake_allowed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.username} - {self.quiz_id}"
    

class QuizSubmissionRecord(models.Model):
    quiz_id = models.CharField(max_length=100)
    quiz_title = models.CharField(max_length=255)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    max_score = models.IntegerField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    quiz_last_updated = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.username} - {self.quiz_title}: {self.score}/{self.max_score}"
                        