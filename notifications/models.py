from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):

    NOTIFICATION_TYPE = [
        ("personal", "Personal"),
        ("broadcast", "Broadcast"),
    ]


    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=100,
        default="Notification"
    )

    message = models.CharField(
        max_length=255
    )

    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPE,
        default="personal"
    )

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):
        return self.title