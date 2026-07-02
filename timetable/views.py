from django.shortcuts import render, redirect, get_object_or_404

from .models import Timetable
from .forms import TimetableForm

from students.models import Student
from teachers.models import Teacher
from collections import OrderedDict

def timetable_list(request):

    timetables = Timetable.objects.select_related(
        "course",
        "teacher"
    ).order_by(
        "day",
        "start_time"
    )

    context = {
        "timetables": timetables
    }

    return render(
        request,
        "timetable/timetable_list.html",
        context
    )

def timetable_create(request):

    if request.method == "POST":

        form = TimetableForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("timetable-list")
        else:
            print("=" * 50)
            print(form.errors)
            print(form.non_field_errors())
            print("=" * 50)

    else:
        form = TimetableForm()

    return render(
        request,
        "timetable/timetable_form.html",
        {"form": form}
    )

def timetable_update(request, pk):

    timetable = get_object_or_404(
        Timetable,
        pk=pk
    )

    if request.method == "POST":

        form = TimetableForm(
            request.POST,
            instance=timetable
        )

        if form.is_valid():
            form.save()
            return redirect("timetable-list")

    else:

        form = TimetableForm(
            instance=timetable
        )

    context = {
        "form": form
    }

    return render(
    request,
    "timetable/timetable_form.html",
    context
)

def timetable_delete(request, pk):

    timetable = get_object_or_404(
        Timetable,
        pk=pk
    )

    if request.method == "POST":

        timetable.delete()

        return redirect("timetable-list")

    context = {
        "timetable": timetable
    }

    return render(
        request,
        "timetable/timetable_delete.html",
        context
    )

def student_timetable(request):

    student = get_object_or_404(
        Student,
        user=request.user
    )

    timetables = Timetable.objects.filter(
        course__in=student.courses.all()
    ).select_related(
        "course",
        "teacher"
    ).order_by(
        "day",
        "start_time"
    )

    context = {
        "timetables": timetables
    }

    return render(
        request,
        "timetable/student_timetable.html",
        context
    )

def teacher_timetable(request):

    teacher = get_object_or_404(
        Teacher,
        user=request.user
    )

    timetables = Timetable.objects.filter(
        teacher=teacher
    ).select_related(
        "course"
    ).order_by(
        "day",
        "start_time"
    )

    context = {
        "timetables": timetables
    }

    return render(
        request,
        "timetable/teacher_timetable.html",
        context
    )

from collections import defaultdict
from django.shortcuts import render, get_object_or_404
from teachers.models import Teacher

def weekly_timetable(request):

    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ]

    grid = defaultdict(list)


    if hasattr(request.user, "teacher"):

        timetables = Timetable.objects.filter(
            teacher__user=request.user
        )


    else:

        student = get_object_or_404(
            Student,
            user=request.user
        )

        timetables = Timetable.objects.filter(
            course__in=student.courses.all()
        )


    timetables = timetables.select_related(
        "course",
        "teacher"
    )


    for t in timetables:

        grid[t.day].append({

            "time": t.start_time.strftime("%H:%M"),

            "end": t.end_time.strftime("%H:%M"),

            "course": t.course,

            "teacher": t.teacher,

            "classroom": t.classroom,

        })


    return render(
        request,
        "timetable/weekly_timetable.html",
        {
            "days": days,
            "grid": dict(grid),
        }
    )