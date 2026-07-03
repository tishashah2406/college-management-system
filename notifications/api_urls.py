from django.urls import path
from .api_views import NotificationListAPIView, NotificationDetailAPIView,MarkAllNotificationsReadAPIView,NotificationDeleteAPIView,DeleteAllNotificationsAPIView,UnreadNotificationAPIView,NotificationCountAPIView


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

    path(
    "mark-all-read/",
    MarkAllNotificationsReadAPIView.as_view(),
    name="mark-all-read-api"
    ),

    path(
    "<int:id>/delete/",
    NotificationDeleteAPIView.as_view(),
    name="notification-delete-api"
   ),

    path(
    "delete-all/",
    DeleteAllNotificationsAPIView.as_view(),
    name="delete-all-notifications-api"
   ),

   path(
    "unread/",
    UnreadNotificationAPIView.as_view(),
    name="unread-notification-api"
   ),

   path(
    "count/",
    NotificationCountAPIView.as_view(),
    name="notification-count-api"
   )


]