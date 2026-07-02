from django.contrib import admin
from django.urls import path
from django.http import JsonResponse

from .models import Timetable
from teachers.models import Teacher


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):

    list_display = (
        "course",
        "teacher",
        "day",
        "start_time",
        "end_time",
    )

    class Media:
        js = (
        "timetable/js/timetable_teacher.js",
    )


    def get_urls(self):

        urls = super().get_urls()

        custom_urls = [
            path(
                    "get-teachers/",
                    self.get_teachers,
                    name="get-teachers"
                ),
        ]

        return custom_urls + urls


    def get_teachers(self, request):

        course_id = request.GET.get("course")

        teachers = Teacher.objects.filter(
            courses__id=course_id
        )

        data = [
            {
                "id": t.id,
                "name": str(t)
            }
            for t in teachers
        ]

        return JsonResponse(data, safe=False)