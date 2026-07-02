from django.urls import path
from . import views


urlpatterns = [
    path("", views.timetable_list, name="timetable-list"),
    path("add/", views.timetable_create, name="timetable-create"),
    path("edit/<int:pk>/", views.timetable_update, name="timetable-update"),
    path("delete/<int:pk>/", views.timetable_delete, name="timetable-delete"),
    path("student/", views.student_timetable, name="student-timetable"),
    path("teacher/", views.teacher_timetable, name="teacher-timetable"),
    path("weekly/",views.weekly_timetable,name="weekly_timetable"),
]