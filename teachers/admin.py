from django.contrib import admin
from .models import Teacher
from .models import TeacherLeave

from .models import TeacherSalary

admin.site.register(TeacherLeave)
admin.site.register(Teacher)

admin.site.register(TeacherSalary)