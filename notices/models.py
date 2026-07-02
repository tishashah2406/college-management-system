from django.db import models
from django.contrib.auth.models import User
from teachers.models import Teacher
from courses.models import Course
class Notice(models.Model):

    NOTICE_TYPE = [
        ("GENERAL", "General"),
        ("EXAM", "Exam"),
        ("EVENT", "Event"),
        ("HOLIDAY", "Holiday"),
        ("URGENT", "Urgent"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()

    notice_type = models.CharField(
        max_length=20,
        choices=NOTICE_TYPE,
        default="GENERAL"
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    expiry_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    is_admin_notice = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
from django.utils import timezone


class NoticeRead(models.Model):

    notice = models.ForeignKey(
        Notice,
        on_delete=models.CASCADE,
        related_name="read_status"
    )


    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notice_reads"
    )


    is_read = models.BooleanField(
        default=False
    )


    read_at = models.DateTimeField(
        null=True,
        blank=True
    )


    class Meta:

        unique_together = (
            "notice",
            "user"
        )


    def mark_read(self):

        self.is_read = True
        self.read_at = timezone.now()
        self.save()


    def __str__(self):

        return f"{self.user.username} - {self.notice.title}"