from django.shortcuts import render
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from teachers.models import Teacher
from .models import Notice, NoticeRead



def notice_board(request):

    notices = Notice.objects.filter(
        expiry_date__gte=timezone.now().date()
    )

    return render(
        request,
        "notices/notice_board.html",
        {
            "notices": notices
        }
    )

@login_required
def teacher_create_notice(request):

    teacher = Teacher.objects.get(
        user=request.user
    )


    if request.method == "POST":


        title = request.POST.get("title")
        description = request.POST.get("description")
        notice_type = request.POST.get("notice_type")

        course_id = request.POST.get("course")

        expiry_date = request.POST.get("expiry_date")


        course = teacher.courses.get(
            id=course_id
        )


        notice = Notice.objects.create(

            title=title,

            description=description,

            notice_type=notice_type,

            created_by=request.user,

            teacher=teacher,

            course=course,

            expiry_date=expiry_date,

            is_admin_notice=False
        )



        students = Student.objects.filter(
            courses=course
        )


        for student in students:

            NoticeRead.objects.create(

                notice=notice,

                user=student.user

            )



        return redirect(
            "teacher_notice_board"
        )


    return render(
        request,
        "notices/teacher_create_notice.html",
        {
            "courses":
            teacher.courses.all()
        }
    )

from django.db.models import Q

@login_required
def teacher_notice_board(request):

    teacher = Teacher.objects.get(user=request.user)


    notices = Notice.objects.filter(

        Q(is_admin_notice=True)

        |

        Q(
            teacher=teacher,
            is_admin_notice=False
        ),

        expiry_date__gte=timezone.now().date()

    ).order_by("-created_at")


    # mark teacher notices as read
    NoticeRead.objects.filter(
        user=request.user,
        notice__in=notices,
        is_read=False
    ).update(
        is_read=True,
        read_at=timezone.now()
    )


    return render(
        request,
        "notices/notice_board.html",
        {
            "notices": notices,
            "is_teacher": True,
        }
    )
from students.models import Student
from .models import Notice, NoticeRead
from django.utils import timezone


from .models import Notice, NoticeRead
from django.utils import timezone
from django.db.models import Q
from students.models import Student


@login_required
def student_notice_board(request):

    student = Student.objects.get(user=request.user)

    notices = Notice.objects.filter(

        Q(is_admin_notice=True)
        |
        Q(
            course__in=student.courses.all(),
            is_admin_notice=False
        ),

        expiry_date__gte=timezone.now().date()

    ).distinct().order_by("-created_at")


    # mark all displayed notices as read
    NoticeRead.objects.filter(
        user=request.user,
        notice__in=notices,
        is_read=False
    ).update(
        is_read=True,
        read_at=timezone.now()
    )


    return render(
        request,
        "notices/notice_board.html",
        {
            "notices": notices,
            "is_teacher": False,
        }
    )

@login_required
def read_notice(request,id):


    read = NoticeRead.objects.filter(

        notice_id=id,

        user=request.user

    ).first()



    if read:

        read.is_read = True

        read.read_at = timezone.now()

        read.save()



    return redirect(
        "student_notice_board"
    )