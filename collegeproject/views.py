from django.shortcuts import render
from students.models import Student
from teachers.models import Teacher
from courses.models import Course

def home(request):

    student = None
    teacher = None
    is_student = False
    is_teacher = False

    if request.user.is_authenticated:

        if request.user.groups.filter(name='Student').exists():
            student = Student.objects.filter(user=request.user).first()
            is_student = True

            recent_students = [student] if student else []
            recent_teachers = Teacher.objects.none()

        elif request.user.groups.filter(name='Teacher').exists():
            teacher = Teacher.objects.filter(user=request.user).first()
            is_teacher = True

            #  Teacher can see data
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

    context = {
        'students_count': students_count,
        'teachers_count': teachers_count,
        'courses_count': courses_count,

        'recent_students': recent_students,
        'recent_teachers': recent_teachers,

        'student': student,
        'teacher': teacher,
        'is_student': is_student,
        'is_teacher': is_teacher,
    }

    return render(request, 'home.html', context)

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