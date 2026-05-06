from django.urls import path
from . import views


urlpatterns = [
    path('', views.teacher_list, name='teacher_list'),
    path('add/', views.teacher_create, name='teacher_create'),
    path('edit/<int:pk>/', views.teacher_update, name='teacher_update'),
    path('delete/<int:pk>/', views.teacher_delete, name='teacher_delete'),
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('leave/apply/', views.apply_leave, name='apply_leave'),
    path('<int:teacher_id>/remove_student/<int:student_id>/<int:course_id>/',views.remove_student_from_course, name='remove_student_from_course'),
    path('<int:teacher_id>/profile/',views.teacher_profile,name='teacher_profile'),
    path('<int:teacher_id>/edit_profile/',views.edit_teacher_profile,name='edit_teacher_profile'),
    path('<int:teacher_id>/enroll_student/', views.enroll_student, name='enroll_student'),
    path('<int:teacher_id>/courseprogress/',views.course_progress,name='course_progress'),
    path('update-progress/<int:student_id>/<int:course_id>/<int:teacher_id>/', views.update_progress, name='update_progress'),
    path('remove-progress/<int:student_id>/<int:course_id>/', views.remove_progress, name='remove_progress'),
    path('attendance/mark/', views.mark_attendance, name='mark_attendance'),
    path('attendance/dashboard/', views.attendance_dashboard, name='attendance_dashboard'),
    path('ajax/get-students/', views.get_students_by_course, name='get_students_by_course'),
    path('attendance/monthly/', views.monthly_attendance, name='monthly_attendance'),
    path('create-assignment/<int:course_id>/', views.create_assignment, name='create_assignment'),
    path('edit-assignment/<int:assignment_id>/', views.edit_assignment, name='edit_assignment'),
    path('delete-assignment/<int:assignment_id>/', views.delete_assignment, name='delete_assignment'),
    path('grade/<int:assignment_id>/', views.grade_assignment, name='grade_assignment'),
    path('teacher/assignments/', views.teacher_assignments, name='teacher_assignments'),
    path('teacher/submissions/', views.teacher_submissions, name='teacher_submissions'),
    path('teacher/progress/', views.teacher_progress, name='teacher_progress'),

]