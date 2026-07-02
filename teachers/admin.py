from django.contrib import admin
from .models import Teacher
from .models import TeacherLeave

from .models import TeacherSalary

admin.site.register(TeacherLeave)
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "salary",
        "is_approved",
    )

    list_filter = (
        "is_approved",
    )

    search_fields = (
        "name",
        "email",
    )

admin.site.register(TeacherSalary)