from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_list, name='student_list'),
    path('add/', views.student_create, name='student_create'),
    path('edit/<int:pk>/', views.student_update, name='student_update'),
    path('delete/<int:pk>/', views.student_delete, name='student_delete'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/<int:student_id>/', views.student_dashboard, name='student_dashboard_admin'),
    path('<int:student_id>/profile/',views.student_profile,name='student_profile'),
    path('<int:student_id>/edit_profile/', views.edit_student_profile, name='edit_student_profile'),
    path('<int:student_id>/notes/', views.student_notes, name='student_notes'),
    path('<int:student_id>/notes/add/<int:course_id>/', views.add_note, name='add_student_note'),
    path('courseprogress/<int:course_id>/', views.course_progress, name='course_progress'),
    path('attendance/', views.student_attendance_dashboard, name='student_attendance_dashboard'), 
    path('assignments/', views.student_assignments_dashboard, name='student_assignments_dashboard'),
    path('assignments/<int:course_id>/', views.view_assignments, name='view_assignments'),
   path('submit-assignment/<int:course_id>/<int:assignment_id>/',views.submit_assignment,name='submit_assignment'),
   path('submissions/', views.student_submission_dashboard, name='student_submission_dashboard'),
   path('submission/delete/<int:submission_id>/', views.delete_submission, name='student_delete_submission'),
   path('submission/edit/<int:submission_id>/', views.edit_submission, name='student_edit_submission'),
   path('notes/', views.student_notes, name='student_notes'),
 
]