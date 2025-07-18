from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    university = models.CharField(max_length=100, blank=True)
    university_name = models.CharField(max_length=100, blank=True)  # Register number
    year_of_passing = models.CharField(max_length=20, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['university_name', 'year_of_passing'], name='unique_register_per_year')
        ]

class Problem(models.Model):
    DIFFICULTY_CHOICES = (
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    constrains = models.TextField()
    difficulty = models.CharField(max_length = 10, choices=DIFFICULTY_CHOICES, default='Easy')
    tags = models.JSONField(default=list, blank=True)
    time_limit = models.FloatField(default=2.0, help_text="Time limit in seconds for code execution")
    starter_code = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class TestCase(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    input_data = models.TextField()
    expected_output = models.TextField()
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return f"Test Case for {self.problem.title} (Hidden: {self.is_hidden})"
    
class Submission(models.Model):
    VERDICT_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Wrong Answer', 'Wrong Answer'),
        ('Time Limit Exceeded', 'Time Limit Exceeded'),
        ('Compiler Error', 'Compilation Error'),
    )
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='submissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submission')
    code = models.TextField()
    language = models.CharField(max_length=30)
    verdict = models.CharField(max_length=30, choices=VERDICT_CHOICES, default='Pending')
    execution_time = models.FloatField(null=True, blank=True)
    memory = models.IntegerField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission by {self.user.username} for  {self.problem.title} ({self.verdict})" 
    
class SolvedProblem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='solved_problems')
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='solved_by')
    solved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'problem') 
    
