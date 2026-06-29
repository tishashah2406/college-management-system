from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Notification

@login_required
def notification_list(request):

    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'notifications/list.html',
        {
            'notifications': notifications
        }
    )

from django.shortcuts import get_object_or_404, redirect

@login_required
def notification_detail(request, id):

    notification = get_object_or_404(
        Notification,
        id=id,
        user=request.user
    )

    notification.is_read = True
    notification.save()

    return render(
        request,
        'notifications/detail.html',
        {
            'notification': notification
        }
    )