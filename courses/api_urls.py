from django.urls import path
from .api_views import (
    CourseAPI, CourseDetailAPI,
    EnrollAPI, UnenrollAPI,
    ProgressAPI, UpdateProgressAPI,
    NoteAPI, AddNoteAPI,
    AssignmentAPI, AssignmentCreateAPI
)

urlpatterns = [
    path('', CourseAPI.as_view()),
    path('<int:pk>/', CourseDetailAPI.as_view()),

    path('<int:course_id>/enroll/', EnrollAPI.as_view()),
    path('<int:course_id>/unenroll/', UnenrollAPI.as_view()),

    path('<int:course_id>/progress/', ProgressAPI.as_view()),
    path('<int:course_id>/progress/update/', UpdateProgressAPI.as_view()),

    path('<int:course_id>/notes/', NoteAPI.as_view()),
    path('<int:course_id>/notes/add/', AddNoteAPI.as_view()),

    path('<int:course_id>/assignments/', AssignmentAPI.as_view()),
    path('assignments/create/', AssignmentCreateAPI.as_view()),
]