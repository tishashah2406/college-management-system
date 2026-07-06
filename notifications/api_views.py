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
    
class MarkAllNotificationsReadAPIView(APIView):

    def patch(self, request):

        Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(
            is_read=True
        )

        return Response(
            {
                "message": "All notifications marked as read."
            },
            status=status.HTTP_200_OK
        )
    
class NotificationDeleteAPIView(APIView):

    def delete(self, request, id):

        notification = get_object_or_404(
            Notification,
            id=id,
            user=request.user
        )

        notification.delete()

        return Response(
            {
                "message": "Notification deleted successfully."
            },
            status=status.HTTP_204_NO_CONTENT
        )
     
class DeleteAllNotificationsAPIView(APIView):

    def delete(self, request):

        Notification.objects.filter(
            user=request.user
        ).delete()

        return Response(
            {
                "message": "All notifications deleted."
            },
            status=status.HTTP_204_NO_CONTENT
        )
    
class UnreadNotificationAPIView(APIView):

    def get(self, request):

        notifications = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).order_by("-created_at")

        serializer = NotificationSerializer(
            notifications,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

class NotificationCountAPIView(APIView):

    def get(self, request):

        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()

        return Response(
            {
                "unread_notifications": unread_count
            },
            status=status.HTTP_200_OK
        )