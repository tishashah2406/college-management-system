from django.contrib import admin
from .models import Teacher
from .models import TeacherLeave

admin.site.register(TeacherLeave)
admin.site.register(Teacher)
