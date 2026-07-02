from django.utils import timezone
from .models import NoticeRead


def notice_unread_count(request):

    if not request.user.is_authenticated:
        return {}

    count = NoticeRead.objects.filter(
        user=request.user,
        is_read=False,
        notice__expiry_date__gte=timezone.now().date()
    ).count()

    return {
        "notice_unread_count": count
    }