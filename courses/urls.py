from django.urls import path
from . import views
from .views import CourseListCreateAPI, CourseDetailAPI

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('add/', views.add_course, name='add_course'),
    path('<int:course_id>/dashboard/', views.course_dashboard, name='course_dashboard'),
    path('<int:course_id>/remove_teacher/<int:teacher_id>/', views.remove_teacher_from_course, name='remove_teacher_from_course'),
    path('<int:course_id>/remove_student/<int:student_id>/', views.remove_student_from_course, name='remove_student_from_course'),
    path('<int:course_id>/edit/', views.edit_course, name='edit_course'),
    path('course/delete/<int:course_id>/', views.course_delete, name='course_delete'),
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('unenroll/<int:course_id>/', views.unenroll_course, name='unenroll_course'),
    path('update-progress/<int:course_id>/', views.update_progress, name='update_progress'),
    path('<int:course_id>/notes/', views.course_notes, name='course_notes'),
    path('teacher-course-progress/<int:course_id>/', views.teacher_course_progress, name='teacher_course_progress'),
   path('<int:course_id>/assignments/', views.course_assignments, name='course_assignments'),
  path('assignment/<int:pk>/', views.assignment_detail, name='assignment_detail'),
   path('assignment/<int:id>/edit/', views.assignment_edit, name='assignment_edit'),
   path('assignment/create/', views.assignment_create, name='assignment_create'),
     path('<int:course_id>/notes/add/', views.add_note, name='add_note'),
     path('note/delete/<int:note_id>/', views.delete_note, name='delete_note'),
     path('assignment/<int:pk>/confirm-delete/', views.assignment_confirm_delete, name='assignment_confirm_delete'),
      path('api/courses/', CourseListCreateAPI.as_view()),
    path('api/courses/<int:pk>/', CourseDetailAPI.as_view()),

]