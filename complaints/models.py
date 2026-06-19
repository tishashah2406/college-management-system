from django.db import models
from django.contrib.auth.models import User
from students.models import Student
from teachers.models import Teacher
from courses.models import Course


class Complaint(models.Model):

    CATEGORY_CHOICES = (
        ('Fees', 'Fees'),
        ('Technical', 'Technical'),
        ('Hostel', 'Hostel'),
        ('Attendance', 'Attendance'),
        ('Assignment', 'Assignment'),
        ('Subject', 'Subject'),
        ('Other', 'Other'),
    )

    PRIORITY_CHOICES = (
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Urgent', 'Urgent'),
    )

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Rejected', 'Rejected'),
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='Medium'
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField()

    attachment = models.FileField(
        upload_to='complaints/',
        blank=True,
        null=True
    )

    assigned_teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='complaints'
    )

    assigned_admin = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admin_complaints'
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    reply = models.TextField(
        blank=True,
        null=True
    )

    admin_remarks = models.TextField(
        blank=True,
        null=True
    )

    resolved_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"#{self.id} - {self.title}"