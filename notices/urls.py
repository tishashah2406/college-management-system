from django.urls import path
from . import views
from .views import notice_board
from .api_views import NoticeListAPIView



urlpatterns = [


    # HTML

    path(
        "",
        notice_board,
        name="notice-board"
    ),
    path(
        "teacher/create/",
        views.teacher_create_notice,
        name="teacher_create_notice"
    ),

    path(
        "teacher/",
        views.teacher_notice_board,
        name="teacher_notice_board"
    ),

    path(
        "student/",
        views.student_notice_board,
        name="student_notice_board"
    ),


    # API

    path(
        "api/",
        NoticeListAPIView.as_view(),
        name="notice-api"
    ),

]