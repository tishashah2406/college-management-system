from django.shortcuts import render
from django.db.models import Count

from students.models import Student
from teachers.models import Teacher
from courses.models import Course
import json


def home(request):

    student = None
    teacher = None
    is_student = False
    is_teacher = False


    if request.user.is_authenticated:

        if request.user.groups.filter(name='Student').exists():

            student = Student.objects.filter(
                user=request.user
            ).first()

            is_student = True

            recent_students = [student] if student else []
            recent_teachers = Teacher.objects.none()


        elif request.user.groups.filter(name='Teacher').exists():

            teacher = Teacher.objects.filter(
                user=request.user
            ).first()

            is_teacher = True

            recent_students = Student.objects.order_by('-id')[:5]
            recent_teachers = Teacher.objects.order_by('-id')[:5]


        else:

            recent_students = []
            recent_teachers = []


    else:

        recent_students = []
        recent_teachers = []



    students_count = Student.objects.count()
    teachers_count = Teacher.objects.count()
    courses_count = Course.objects.count()



    # =========================
    # CHART DATA
    # =========================



    courses_with_students = Course.objects.all()


    course_names = []
    course_students = []


    for course in courses_with_students:

        count = Student.objects.filter(
            courses=course
        ).count()


        course_names.append(
            course.name
        )

        course_students.append(
            count
        )



    context = {

    'students_count': students_count,
    'teachers_count': teachers_count,
    'courses_count': courses_count,


    'course_names': json.dumps(course_names),

    'course_students': json.dumps(course_students),


    'recent_students': recent_students,
    'recent_teachers': recent_teachers,

    'student': student,
    'teacher': teacher,

    'is_student': is_student,
    'is_teacher': is_teacher,
}

    return render(
        request,
        'home.html',
        context
    )

def about(request):

    return render(
        request,
        'about.html'
    )

def contact(request):

    return render(
        request,
        'contact.html'
    )