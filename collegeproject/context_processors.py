from teachers.models import Teacher
from students.models import Student


def user_role(request):

    context = {
        "is_teacher": False,
        "is_student": False,
        "teacher": None,
        "student": None,
    }

    if request.user.is_authenticated:

        try:
            teacher = Teacher.objects.get(user=request.user)

            context["is_teacher"] = True
            context["teacher"] = teacher

        except Teacher.DoesNotExist:
            pass


        try:
            student = Student.objects.get(user=request.user)

            context["is_student"] = True
            context["student"] = student

        except Student.DoesNotExist:
            pass


    return context

from notices.models import NoticeRead


def notice_count(request):

    if request.user.is_authenticated:

        count = NoticeRead.objects.filter(
            user=request.user,
            is_read=False
        ).count()

        return {
            "unread_notice_count": count
        }


    return {
        "unread_notice_count": 0
    }