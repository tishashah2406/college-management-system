from django.db import models
from courses.models import Course

from django.contrib.auth.models import User
from notifications.models import Notification


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)

    # NEW FIELD
    is_approved = models.BooleanField(default=False)

    courses = models.ManyToManyField(
        Course,
        related_name='assigned_teachers',
        blank=True
    )

    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='teacher_profiles/', blank=True, null=True)

    def __str__(self):
        return self.name
    
from django.db import models
from notifications.models import Notification

class TeacherLeave(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE
    )

    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    applied_at = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):

        old_status = None

        if self.pk:
            old_status = TeacherLeave.objects.get(
                pk=self.pk
            ).status

        super().save(*args, **kwargs)

        # Status changed
        if old_status != self.status:

            if self.status == "Approved":

                Notification.objects.create(
                    user=self.teacher.user,
                    message=f" Leave approved from ({self.start_date} to {self.end_date})"
                )

            elif self.status == "Rejected":

                Notification.objects.create(
                    user=self.teacher.user,
                    message=f" Leave rejected from ({self.start_date} to {self.end_date})"
                )

    def __str__(self):
        return f"{self.teacher.name} - {self.status}"

class TeacherSalary(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    month = models.DateField()

    base_salary = models.DecimalField(max_digits=10, decimal_places=2)

    total_leave_days = models.IntegerField(default=0)
    deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    final_salary = models.DecimalField(max_digits=10, decimal_places=2)

    payment_status = models.CharField(
        max_length=10,
        choices=[
            ('Pending', 'Pending'),
            ('Paid', 'Paid')
        ],
        default='Pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.teacher.name} - {self.month.strftime('%B %Y')}"
    
class TeacherAttendance(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    date = models.DateField()

    status = models.CharField(
        max_length=10,
        choices=[
            ('Present', 'Present'),
            ('Absent', 'Absent')
        ]
    )

class Holiday(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()