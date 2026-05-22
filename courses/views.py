from django.contrib import messages

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Assignment, Course, Note, Submission
from .forms import CourseForm

from teachers.models import Teacher
from students.models import Student, CourseProgress


# ---------------- HOME ----------------
def home(request):
    if request.user.groups.filter(name='Teacher').exists():
        return redirect('teacher_dashboard')

    elif request.user.groups.filter(name='Student').exists():
        return redirect('student_dashboard')

    return redirect('login')


# ---------------- COURSE LIST ----------------
@login_required
def course_list(request):
    user = request.user
    courses = Course.objects.all()

    is_student = user.groups.filter(name='Student').exists()
    can_edit = not is_student

    student = None
    if is_student:
        student = getattr(user, 'student', None)

    return render(request, 'courses/course_list.html', {
        'courses': courses,
        'is_student': is_student,
        'can_edit': can_edit,
        'student': student,
    })

# ---------------- COURSE DASHBOARD ----------------
@login_required
def course_dashboard(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    return render(request, 'courses/course_dashboard.html', {
        'course': course,
        'assigned_teachers': course.assigned_teachers.all(),
        'assigned_students': course.enrolled_students.all(),
    })

# ---------------- REMOVE TEACHER ----------------
def remove_teacher_from_course(request, course_id, teacher_id):
    course = get_object_or_404(Course, id=course_id)
    teacher = get_object_or_404(Teacher, id=teacher_id)

    teacher.courses.remove(course)
    return redirect('course_dashboard', course_id=course.id)

# ---------------- REMOVE STUDENT ----------------
def remove_student_from_course(request, course_id, student_id):
    course = get_object_or_404(Course, id=course_id)
    student = get_object_or_404(Student, id=student_id)

    student.courses.remove(course)
    return redirect('course_dashboard', course_id=course.id)


# ---------------- COURSE CRUD ----------------
@login_required
def add_course(request):
    form = CourseForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('course_list')

    return render(request, 'courses/course_form.html', {'form': form})


@login_required
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    form = CourseForm(request.POST or None, instance=course)

    if form.is_valid():
        form.save()
        return redirect('course_list')

    return render(request, 'courses/course_form.html', {'form': form})


@login_required
def course_delete(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.user.groups.filter(name='Student').exists():
        return redirect('course_list')

    if request.method == "POST":
        course.delete()
        return redirect('course_list')

    return render(request, 'courses/course_confirm_delete.html', {
        'course': course
    })


# ---------------- ENROLL ----------------
@login_required
def enroll_course(request, course_id):
    student = Student.objects.get(user=request.user)
    course = get_object_or_404(Course, id=course_id)

    if not student.courses.filter(id=course.id).exists():
        student.courses.add(course)

    CourseProgress.objects.get_or_create(
        student=student,
        course=course,
        defaults={'progress': 0}
    )

    return redirect('course_list')

def unenroll_course(request, course_id):

    student = Student.objects.get(user=request.user)

    course = get_object_or_404(Course, id=course_id)

    student.courses.remove(course)

    CourseProgress.objects.filter(
        student=student,
        course=course
    ).delete()

    return redirect('course_list')

# ---------------- PROGRESS ----------------
@login_required
def student_course_progress(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    student = Student.objects.get(user=request.user)

    progress, _ = CourseProgress.objects.get_or_create(
        student=student,
        course=course
    )

    return render(request, 'courses/course_progress.html', {
        'course': course,
        'progress': progress
    })

@login_required
def update_progress(request, course_id):
    student = Student.objects.get(user=request.user)

    progress_obj, _ = CourseProgress.objects.get_or_create(
        student=student,
        course_id=course_id
    )

    progress_obj.progress = min(progress_obj.progress + 10, 100)
    progress_obj.save()

    return redirect('student_dashboard', student.id)

@login_required
def teacher_course_progress(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    return render(request, 'courses/course_progress_teacher.html', {
        'course': course,
        'teachers': course.assigned_teachers.all(),
        'students': course.enrolled_students.all(),
    })

@login_required
def teacher_update_progress(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    for student in course.enrolled_students.all():
        progress_obj, _ = CourseProgress.objects.get_or_create(
            student=student,
            course=course
        )

        progress_obj.progress = min(progress_obj.progress + 10, 100)
        progress_obj.save()

    return redirect('teacher_course_progress', course_id=course.id)

# ---------------- NOTES ----------------
@login_required
def course_notes(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    return render(request, 'courses/course_notes.html', {
        'course': course,
        'notes': Note.objects.filter(course_id=course_id).order_by('-uploaded_at'),
        'is_teacher': request.user.groups.filter(name='Teacher').exists(),
    })

@login_required
def add_note(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == "POST":
        Note.objects.create(
            course=course,
            title=request.POST.get('title'),
            file=request.FILES.get('file')
        )
        return redirect('course_notes', course_id=course.id)

    return render(request, 'courses/add_note.html', {'course': course})

@login_required
def delete_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)

    if not request.user.groups.filter(name='Teacher').exists():
        return redirect('course_notes', course_id=note.course.id)

    course_id = note.course.id
    note.delete()

    return redirect('course_notes', course_id=course_id) 
# ---------------- ASSIGNMENTS ----------------
@login_required
def course_assignments(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    return render(request, 'courses/course_assignments.html', {
        'course': course,
        'assignments': Assignment.objects.filter(course=course),
    })

def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)

    submission = None

    if request.user.is_authenticated:
        student = getattr(request.user, 'student', None)
        if student:
            submission = Submission.objects.filter(
                student=student,
                assignment=assignment
            ).first()

    return render(request, 'courses/assignment_detail.html', {
        'assignment': assignment,
        'submission': submission
    })

def assignment_edit(request, id):
    assignment = get_object_or_404(Assignment, id=id)

    if request.method == "POST":
        assignment.title = request.POST.get('title')
        assignment.save()
        return redirect('course_assignments', course_id=assignment.course.id)

    return render(request, 'assignment_edit.html', {'assignment': assignment})

def assignment_create(request):
    courses = Course.objects.all()

    if request.method == "POST":
        title = request.POST.get('title')
        course_id = request.POST.get('course')
        due_date = request.POST.get('due_date')
        description = request.POST.get('description')

        #  Validation
        if not title or not course_id:
            messages.error(request, "Title and Course are required")
            return render(request, 'courses/assignment_create.html', {
                'courses': courses
            })

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            messages.error(request, "Invalid course selected")
            return render(request, 'courses/assignment_create.html', {
                'courses': courses
            })

        #  Create assignment
        assignment = Assignment.objects.create(
            title=title,
            course=course,
            due_date=due_date if due_date else None,
            description=description
        )

        messages.success(request, "Assignment created successfully")

        return redirect('course_assignments', course_id=course.id)

    return render(request, 'courses/assignment_create.html', {
        'courses': courses
    })

def assignment_confirm_delete(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)

    if request.method == "POST":
        assignment.delete()
        return redirect('assignment_list')

    return render(request, 'courses/assignment_confirm_delete.html', {
        'assignment': assignment
    })

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Course
from .serializers import CourseSerializer

class CourseListCreateAPI(APIView):

    def get(self, request):
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CourseSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CourseDetailAPI(APIView):

    def get(self, request, pk):
        course = get_object_or_404(Course, id=pk)
        serializer = CourseSerializer(course)
        return Response(serializer.data)

    def put(self, request, pk):
        course = get_object_or_404(Course, id=pk)
        serializer = CourseSerializer(course, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors)

    def delete(self, request, pk):
        course = get_object_or_404(Course, id=pk)
        course.delete()
        return Response({"message": "Deleted successfully"})