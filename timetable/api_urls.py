from django.urls import path

from .api_views import (
    CreateTimetableAPIView,
    TimetableListAPIView,
    StudentTimetableAPIView,
    TeacherTimetableAPIView,
    UpdateTimetableAPIView,
    DeleteTimetableAPIView,
)


urlpatterns = [

    path(
        "create/",
        CreateTimetableAPIView.as_view(),
        name="api-create-timetable"
    ),

    path(
        "list/",
        TimetableListAPIView.as_view(),
        name="api-timetable-list"
    ),

    path(
        "student/",
        StudentTimetableAPIView.as_view(),
        name="api-student-timetable"
    ),

    path(
        "teacher/",
        TeacherTimetableAPIView.as_view(),
        name="api-teacher-timetable"
    ),

    path(
        "update/<int:pk>/",
        UpdateTimetableAPIView.as_view(),
        name="api-update-timetable"
    ),

    path(
        "delete/<int:pk>/",
        DeleteTimetableAPIView.as_view(),
        name="api-delete-timetable"
    ),

]