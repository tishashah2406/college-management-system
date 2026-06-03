from django.db import models
from courses.models import Course, Assignment
from django.contrib.auth.models import User


# ===================== STUDENT =====================
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    age = models.IntegerField()

    courses = models.ManyToManyField(
        Course,
        related_name='enrolled_students',
        blank=True
    )

    profile_pic = models.ImageField(
        upload_to='profile_pics/',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name


# ===================== COURSE PROGRESS =====================
class CourseProgress(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="progress"
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="progress"
    )

    progress = models.IntegerField(default=0)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.name} - {self.course.name} ({self.progress}%)"


# ===================== ATTENDANCE =====================
class Attendance(models.Model):
    STATUS_CHOICES = (
        ('Present', 'Present'),
        ('Absent', 'Absent'),
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="attendance"
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="attendance"
    )

    date = models.DateField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Absent'
    )

    class Meta:
        unique_together = ('student', 'course', 'date')

    def __str__(self):
        return f"{self.student.name} - {self.course.name} - {self.date} ({self.status})"

# ===================== SUBMISSION =====================
class Submission(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="submissions")
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions")
    content = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='submissions/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.IntegerField(null=True, blank=True)


    class Meta:
        db_table = 'students_submission'   