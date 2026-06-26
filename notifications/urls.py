# notifications/urls.py

from django.urls import path
from .views import notification_list, notification_detail

urlpatterns = [

    path(
        '',
        notification_list,
        name='notifications'
    ),

    path(
        '<int:id>/',
        notification_detail,
        name='notification_detail'
    ),

]