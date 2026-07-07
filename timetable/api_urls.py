from django.urls import path

from .api_views import (
    CreateTimetableAPIView,
    TimetableListAPIView,
    StudentTimetableAPIView,
    TeacherTimetableAPIView,
    UpdateTimetableAPIView,
    DeleteTimetableAPIView,
    TimetableDetailAPIView,
    PartialUpdateTimetableAPIView,
    CourseTimetableAPIView,
    DayTimetableAPIView,TeacherTimetableByIdAPIView,RoomTimetableAPIView,TodayTimetableAPIView,SearchTimetableAPIView
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

    path(
        "<int:pk>/",
        TimetableDetailAPIView.as_view(),
        name="timetable-detail-api"
    ),

    path(
        "<int:pk>/patch/",
        PartialUpdateTimetableAPIView.as_view(),
        name="patch-timetable-api"
    ),

    path(
        "course/<int:course_id>/",
        CourseTimetableAPIView.as_view(),
        name="course-timetable-api"
    ),

    path(
        "day/<str:day>/",
        DayTimetableAPIView.as_view(),
        name="day-timetable-api"
    ),
    
    path(
        "teacher/<int:teacher_id>/",
        TeacherTimetableByIdAPIView.as_view(),
        name="teacher-id-timetable-api"
    ),

    path(
        "room/<str:room>/", 
        RoomTimetableAPIView.as_view(), 
        name="room-timetable-api"
    ),

    path(
        "today/", 
        TodayTimetableAPIView.as_view(),
        name="today-timetable-api"
    ),

    path(
        "search/", 
        SearchTimetableAPIView.as_view(), 
        name="search-timetable-api"
    ),
]