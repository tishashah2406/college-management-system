from .models import Notification


def notification_data(request):

    if request.user.is_authenticated:

        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()

        recent_notifications = Notification.objects.filter(
            user=request.user
        )[:5]

        return {
            'unread_count': unread_count,
            'recent_notifications': recent_notifications
        }

    return {}