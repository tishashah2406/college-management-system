from django.contrib import admin
from students.models import Student
from .models import Submission

admin.site.register(Student)



admin.site.register(Submission)