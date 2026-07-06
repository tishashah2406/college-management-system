from django.urls import path
from . import views
from .views import notice_board
from .api_views import (
    NoticeListAPIView,
    NoticeDetailAPIView,
    CreateNoticeAPIView,UpdateNoticeAPIView
)


from . import views


urlpatterns = [


    path(
        "",
        views.notice_board,
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


    path(
        "read/<int:id>/",
        views.read_notice,
        name="read_notice"
    ),



    # API

    path(
        "api/",
        NoticeListAPIView.as_view(),
        name="notice-api"
    ),

    path("notices/", NoticeListAPIView.as_view(), name="notice-list-api"),
    path("notices/<int:id>/", NoticeDetailAPIView.as_view(), name="notice-detail-api"),
    path("create/", CreateNoticeAPIView.as_view()),
    path("<int:id>/update/", UpdateNoticeAPIView.as_view()),


]