from django.db import models
from courses.models import Course
from teachers.models import Teacher


class Timetable(models.Model):

    DAYS = [
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
        ("Saturday", "Saturday"),
    ]

    day = models.CharField(
        max_length=20,
        choices=DAYS
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="timetables"
    )

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="timetables"
    )

    classroom = models.CharField(max_length=30)

    start_time = models.TimeField()

    end_time = models.TimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["day", "start_time"]

    def __str__(self):
        return f"{self.course.name} - {self.day}"