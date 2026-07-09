from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from .models import Notification
from .Serializers import NotificationSerializer


class NotificationViewSet(ModelViewSet):

    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        ).order_by("-created_at")

    def retrieve(self, request, *args, **kwargs):

        notification = self.get_object()

        if not notification.is_read:
            notification.is_read = True
            notification.save()

        serializer = self.get_serializer(notification)

        return Response(serializer.data)

    @action(detail=False, methods=["patch"])
    def mark_all_read(self, request):

        self.get_queryset().filter(
            is_read=False
        ).update(
            is_read=True
        )

        return Response(
            {
                "message": "All notifications marked as read."
            }
        )

    @action(detail=False, methods=["delete"])
    def delete_all(self, request):

        self.get_queryset().delete()

        return Response(
            {
                "message": "All notifications deleted."
            }
        )

    @action(detail=False, methods=["get"])
    def unread(self, request):

        notifications = self.get_queryset().filter(
            is_read=False
        )

        serializer = self.get_serializer(
            notifications,
            many=True
        )

        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def count(self, request):

        notifications = self.get_queryset()

        return Response(
            {
                "total_notifications": notifications.count(),
                "read_notifications": notifications.filter(
                    is_read=True
                ).count(),
                "unread_notifications": notifications.filter(
                    is_read=False
                ).count(),
            }
        )