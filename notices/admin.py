from django.contrib import admin
from .models import Notice, NoticeRead
from students.models import Student
from teachers.models import Teacher


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):

    exclude = (
        "created_by",
        "teacher",
        "course",
    )


    def save_model(self, request, obj, form, change):

        obj.created_by = request.user
        obj.is_admin_notice = True

        super().save_model(
            request,
            obj,
            form,
            change
        )


        if not change:

            # Students unread
            for student in Student.objects.all():

                NoticeRead.objects.get_or_create(
                    notice=obj,
                    user=student.user
                )


            # Teachers unread
            for teacher in Teacher.objects.all():

                NoticeRead.objects.get_or_create(
                    notice=obj,
                    user=teacher.user
                )


@admin.register(NoticeRead)
class NoticeReadAdmin(admin.ModelAdmin):

    list_display = (
        "notice",
        "user",
        "is_read",
        "read_at"
    )