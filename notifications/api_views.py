from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

from .models import Notification
from .Serializers import NotificationSerializer


class NotificationListAPIView(APIView):

    def get(self, request):

        notifications = Notification.objects.filter(
            user=request.user
        ).order_by("-created_at")

        serializer = NotificationSerializer(
            notifications,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class NotificationDetailAPIView(APIView):

    def get(self, request, id):

        notification = get_object_or_404(
            Notification,
            id=id,
            user=request.user
        )

        notification.is_read = True
        notification.save()

        serializer = NotificationSerializer(
            notification
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )