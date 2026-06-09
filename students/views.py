from datetime import datetime
from importlib.resources import contents

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q

from courses.serializers import AssignmentSerializer, CourseProgressSerializer, CourseSerializer,SubmissionSerializer
from .models import Student, Submission
from .forms import StudentForm
from courses.models import Assignment, Course, Note
from teachers.models import Teacher
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from students.models import CourseProgress
from .serializers import StudentSerializer

def student_list(request):
    query = request.GET.get('q')
    course_filter = request.GET.get('course')
    students = Student.objects.all()

    if query:
        students = students.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(age__icontains=query) |
            Q(courses__name__icontains=query)
        ).distinct()

    if course_filter:
        students = students.filter(courses__id=course_filter)

    all_courses = Course.objects.all()

    return render(request, 'students/student_list.html', {
        'students': students,
        'all_courses': all_courses,
        'query': query  or "",
        'selected_course': course_filter or ""
    })

@login_required
def student_create(request):

    form = StudentForm(request.POST or None)

    if form.is_valid():
        student = form.save(commit=False)

        # create username from email
        username = student.email.split('@')[0]

        # default password
        password = "12345"

        # create Django user
        user = User.objects.create_user(
            username=username,
            password=password
        )

        # add user to Student group
        group = Group.objects.get(name="Student")
        user.groups.add(group)

        # connect user with student
        student.user = user
        student.save()

        form.save_m2m()

        return redirect('student_list')

    return render(request, 'students/student_form.html', {'form': form})

@login_required
def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)

        if form.is_valid():
            form.save()
            messages.success(request, "Student updated successfully")
            return redirect('student_list')
        else:
            messages.error(request, "Please correct the errors below")

    else:
        form = StudentForm(instance=student)

    return render(request, 'students/student_form.html', {'form': form})

@login_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        student.delete()
        return redirect('student_list')
    return render(request, 'students/student_confirm_delete.html', {'student': student})

from django.http import HttpResponse, HttpResponseForbidden
from .models import Attendance

@login_required
def student_dashboard(request, student_id=None):

    if student_id:
        student = get_object_or_404(Student, id=student_id)
    else:
        student = Student.objects.filter(user=request.user).first()
        if not student:
            return render(request, 'students/error.html', {
                'message': 'Student profile not found. Please contact admin.'
            })

    courses = student.courses.all()
    teachers = Teacher.objects.filter(courses__in=courses).distinct()

    progress_list = []
    for course in courses:
        progress_obj, _ = CourseProgress.objects.get_or_create(
            student=student,
            course=course
        )
        progress_list.append(progress_obj)

    attendance_per_course = {}
    for course in courses:
        attendance_per_course[course] = Attendance.objects.filter(
            student=student,
            course=course
        ).order_by('-date')

    total = Attendance.objects.filter(student=student).count()
    present = Attendance.objects.filter(student=student, status="Present").count()
    absent = Attendance.objects.filter(student=student, status="Absent").count()

    students_count = Student.objects.count()
    teachers_count = Teacher.objects.count()
    courses_count = Course.objects.count()

    assignment_count = Assignment.objects.count()

    submission_count = Submission.objects.filter(student=student).count()

    graded_count = Submission.objects.filter(
        student=student,
        grade__isnull=False
    ).count()

    ungraded_count = Submission.objects.filter(
        student=student,
        grade__isnull=True
    ).count()
    return render(request, 'students/student_dashboard.html', {

        'student': student,
        'courses': courses,
        'teachers': teachers,
        'progress_list': progress_list,

        'attendance_per_course': attendance_per_course,
        'total': total,
        'present': present,
        'absent': absent,

        'students_count': students_count,
        'teachers_count': teachers_count,
        'courses_count': courses_count,

        'assignment_count': assignment_count,
        'submission_count': submission_count,
        'graded_count': graded_count,
        'ungraded_count': ungraded_count,
    })

#---------student profile----------------
@login_required
def student_profile(request, student_id):

    if not student_id:
        return redirect('student_list')

    student = get_object_or_404(Student, id=student_id, user=request.user)

    if request.method == "POST":
        if request.FILES.get('profile_pic'):
            student.profile_pic = request.FILES['profile_pic']
            student.save()

        return redirect('student_profile', student_id=student.id)

    return render(request, 'students/student_profile.html', {
        'student': student,
        'courses': student.courses.all()
    })

#-----------------edit profile-----------------
@login_required
def edit_student_profile(request, student_id):
    student = get_object_or_404(Student, id=student_id, user=request.user)
    available_courses = Course.objects.all()

    if request.method == "POST":
        student.name = request.POST.get("name")

        age = request.POST.get("age")
        if age:
            student.age = int(age)

        email = request.POST.get("email")
        if email:
            student.user.email = email
            student.user.save()

        #  NEW: handle profile picture upload
        if request.FILES.get('profile_pic'):
            student.profile_pic = request.FILES['profile_pic']

        student.save()

        # update courses
        course_ids = request.POST.getlist('courses')
        student.courses.set(course_ids)

        return redirect('student_profile', student_id=student.id)

    return render(request, 'students/edit_students_profile.html', {
        'student': student,
        'available_courses': available_courses
    })

#--------notes-----------------
@login_required
def student_notes(request):

    student = get_object_or_404(Student, user=request.user)

    courses = student.courses.all()

    return render(request, 'students/student_notes.html', {
        'student': student,
        'courses': courses
    })

#-----------------add note-----------------
@login_required
def add_note(request, student_id, course_id):
    student = get_object_or_404(Student, id=student_id, user=request.user)
    course = get_object_or_404(Course, id=course_id)

    if request.method == "POST":
        content = request.POST.get("content")
        Note.objects.create(course=course, content=content)
        return redirect('student_notes', student_id=student.id)

    return render(request, 'students/add_note.html', {
        'student': student,
        'course': course
    })

#-------------delete note--------------------------
@login_required
def delete_note(request,student_id,course_id,note_id):
    student=get_object_or_404(Student,id=student_id, user=request.user)
    note = get_object_or_404(Note,id=note_id,course_id=course_id)

    if request.method =="POST":
        note.delete()
        return redirect('student_notes',student_id=student.id)
    
    return render(request,'students/delete_note.html',{
        'note':note
    })

#---------------course progress----------------------
@login_required
def course_progress(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    students = course.enrolled_students.all()

    return render(request, 'courses/course_progress.html', {
        'course': course,
        'students':students
    })

@login_required
def student_attendance_dashboard(request):
    student = Student.objects.filter(user=request.user).first()
    if not student:
        return render(request, 'students/error.html', {
            'message': 'Student profile not found.'
        })

    courses = student.courses.all()

    # Get filter values from GET params
    selected_course_id = request.GET.get('course')
    month_input = request.GET.get('month')  
    if not month_input:
        month_input = datetime.now().strftime('%Y-%m')

    year, month = month_input.split('-')

    # Filter attendance per course
    attendance_data = []
    for course in courses:
        if selected_course_id and int(selected_course_id) != course.id:
            continue  

        records = Attendance.objects.filter(
            student=student,
            course=course,
            date__year=int(year),
            date__month=int(month)
        ).order_by('-date')

        total = records.count()
        present = records.filter(status="Present").count()
        absent = records.filter(status="Absent").count()

        attendance_data.append({
            'course': course,
            'records': records,
            'total': total,
            'present': present,
            'absent': absent
        })

    return render(request, 'students/student_attendance_dashboard.html', {
        'student': student,
        'courses': courses,
        'attendance_data': attendance_data,
        'selected_course_id': selected_course_id,
        'month_input': month_input
    })

from django.utils import timezone
from django.contrib import messages

@login_required
def submit_assignment(request, course_id, assignment_id):
    student = get_object_or_404(Student, user=request.user)

    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        course_id=course_id
    )

    # ADD THIS BLOCK (VERY IMPORTANT)
    if timezone.now().date() > assignment.due_date:
        messages.error(request, "Deadline has passed. You cannot submit this assignment.")
        return redirect('view_assignments', course_id=course_id)

    if request.method == "POST":
        content = request.POST.get('content')
        file = request.FILES.get('file')

        #  if BOTH empty → reject
        if not content and not file:
            messages.error(request, "Please add content or upload a file.")
            return redirect('submit_assignment', course_id=course_id, assignment_id=assignment_id)

        Submission.objects.create(
            student=student,
            assignment=assignment,
            content=content,
            file=file
        )

        messages.success(request, "Assignment submitted successfully!")

        return redirect('view_assignments', course_id=course_id)

    return render(request, 'students/submit_assignment.html', {
        'course': assignment.course,
        'assignment': assignment
    })

@login_required
def view_assignments(request, course_id):
    student = get_object_or_404(Student, user=request.user)
    course = get_object_or_404(Course, id=course_id)

    assignments = Assignment.objects.filter(course=course)

    submissions = Submission.objects.filter(student=student)

    return render(request, 'students/view_assignments.html', {
        'course': course,
        'student': student,
        'assignments': assignments,
        'submissions': submissions
    })

@login_required
def student_assignments_dashboard(request):
    student = get_object_or_404(Student, user=request.user)
    courses = student.courses.all()

    return render(request, 'students/student_assignments_dashboard.html', {
        'student': student,
        'courses': courses
    })

def student_assignment_detail(request,course_id,assignment_id):
    student = get_object_or_404(Student,user=request.user)
    course = get_object_or_404(Course,id=course_id)
    assignment = get_object_or_404(Assignment,id=assignment_id,course=course)
    submission = Submission.objects.filter(student=student,assignment=assignment).first()

    return render(request,'students/student_assignment_detail.html',{
        'course':course,
        'assignment':assignment,
        'submission':submission
    })

@login_required
def view_submissions(request,course_id,assignment_id):
    student = get_object_or_404(Student,user=request.user)
    course = get_object_or_404(Course,id=course_id)
    assignment = get_object_or_404(Assignment,id=assignment_id,course=course)
    submission = Submission.objects.filter(student=student,assignment=assignment).first()

    return render(request,'students/view_submission.html',{
        'course':course,
        'assignment':assignment,
        'submission':submission
    })

def view_grades(request,course_id,assignments_id):
    student = get_object_or_404(Student,user=request.user)
    course = get_object_or_404(Course,id=course_id)
    assignments = get_object_or_404(Assignment,id=assignments_id,course=course)
    submission = Submission.objects.filter(student=student,assignment=assignments).first()

    return render(request,'students/view_grades.html',{
        'course':course,
        'assignments':assignments,
        'submission':submission
    })

@login_required
def student_submission_dashboard(request):
    student= get_object_or_404(Student,user=request.user)
    submissions =Submission.objects.filter(student=student).select_related('assignment__course')

    return render(request,'students/student_submission_dashboard.html',{
        'student':student,
        'submissions':submissions
    })

@login_required
def delete_submission(request, submission_id):
    student = get_object_or_404(Student, user=request.user)
    submission = get_object_or_404(Submission, id=submission_id, student=student)

    if request.method == "POST":
        submission.delete()
        return redirect('student_submission_dashboard')

    return render(request, 'students/delete_submission.html', {
        'submission': submission
    })

@login_required
def edit_submission(request, submission_id):
    student = get_object_or_404(Student, user=request.user)
    submission = get_object_or_404(Submission, id=submission_id, student=student)

    if request.method == "POST":
        content = request.POST.get('content')
        file = request.FILES.get('file')

        submission.content = content

        if file:
            submission.file = file

        submission.save()
        return redirect('student_submission_dashboard')

    return render(request, 'students/edit_submission.html', {
        'submission': submission
    })     