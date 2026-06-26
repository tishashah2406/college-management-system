from django.urls import path
from .api_views import NotificationListAPIView, NotificationDetailAPIView

urlpatterns = [
    path(
        "",
        NotificationListAPIView.as_view(),
        name="notification-list-api"
    ),

    path(
        "<int:id>/",
        NotificationDetailAPIView.as_view(),
        name="notification-detail-api"
    ),
]