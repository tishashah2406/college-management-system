from django.urls import path
from . import views



urlpatterns=[


path(
'create/',
views.create_complaint,
name="create_complaint"
),


path(
'my/',
views.my_complaints,
name="my_complaints"
),


path(
'teacher/',
views.teacher_complaints,
name="teacher_complaints"
),


path(
'admin/',
views.admin_complaints,
name="admin_complaints"
),


path(
    'resolve/<int:id>/',
    views.resolve_complaint,
    name='resolve_complaint'
),

]