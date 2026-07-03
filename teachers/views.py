from django.contrib import messages
from urllib import request
from xml.dom import ValidationErr
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from teachers.serializers import TeacherSerializer
from .models import Teacher
from .forms import TeacherForm
from courses.models import Course
from students.models import Assignment, Student
from students.models import CourseProgress
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from students.models import Attendance
from django.db.models import Count
from datetime import datetime
from django.http import JsonResponse
from .services import calculate_teacher_salary
from notifications.models import Notification
from timetable.models import Timetable

# ---------------- Teacher List ----------------

def teacher_list(request):
    query = request.GET.get('q', '')
    selected_course = request.GET.get('course', '')

    teachers = Teacher.objects.prefetch_related('courses').all()

    if query:
        teachers = teachers.filter(
            Q(name__icontains=query) | Q(email__icontains=query)
        )

    if selected_course.isdigit():
        teachers = teachers.filter(courses__id=int(selected_course))

    all_courses = Course.objects.all()

    # Student check
    is_student = request.user.groups.filter(name='Student').exists()
    student = getattr(request.user, 'student', None) if is_student else None

    return render(request, 'teachers/teacher_list.html', {
        'teachers': teachers.distinct(),
        'all_courses': all_courses,
        'query': query,
        'selected_course': selected_course,
        'is_student': is_student,
        'student': student,  
    })

# ---------------- Add Teacher ----------------
@login_required
def teacher_create(request):
    form = TeacherForm(request.POST or None)

    if form.is_valid():
        teacher = form.save(commit=False)

        username = teacher.email.split('@')[0]
        password = "12345"

        user = User.objects.create_user(
            username=username,
            password=password,     
        )

        group = Group.objects.get(name="Teacher")
        user.groups.add(group)

        teacher.user = user
        teacher.save()

        form.save_m2m()  

        return redirect('teacher_list')

    return render(request, 'teachers/teacher_form.html', {'form': form})

# ---------------- Edit Teacher ----------------
@login_required
def teacher_update(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    form = TeacherForm(request.POST or None, instance=teacher)
    if form.is_valid():
        teacher = form.save(commit=False)
        teacher.save()
        form.save_m2m()
        return redirect('teacher_list')
    return render(request, 'teachers/teacher_form.html', {'form': form})

# ---------------- Delete Teacher ----------------
@login_required
def teacher_delete(request, pk):

    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == "POST":
        teacher.delete()
        return redirect('teacher_list')
    return render(request, 'teachers/teacher_confirm_delete.html', {'teacher': teacher})

# ---------------- Teacher Dashboard ----------------
from students.models import Submission,Assignment
from django.db import connection

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required
def teacher_dashboard(request):

    # Check Teacher Group
    if request.user.is_superuser:
        return redirect('admin:index')

    if request.user.groups.filter(
        name='Student'
    ).exists():
        return redirect('student_dashboard')

    if not request.user.groups.filter(
        name='Teacher'
    ).exists():

        messages.error(
            request,
            "Access denied"
        )
        return redirect('login')

    # Safe Teacher Fetch
    teacher = Teacher.objects.filter(
        user=request.user
    ).first()

    if not teacher:

        messages.error(
            request,
            "Teacher profile not found"
        )

        return redirect('login')

    # Teacher courses
    courses = teacher.courses.all()

    students = Student.objects.filter(
        courses__in=courses
    ).prefetch_related('courses').distinct()

    # Auto create progress
    for course in courses:

        for student in students.filter(
            courses=course
        ):

            CourseProgress.objects.get_or_create(
                student=student,
                course=course,
                defaults={
                    'progress': 0
                }
            )

    progress_list = CourseProgress.objects.filter(
        course__in=courses
    )

    # Assignments
    assignments = Assignment.objects.filter(
        course__in=courses
    ).distinct()

    # Submissions
    submissions = Submission.objects.filter(
        assignment__course__in=courses
    ).select_related(
        'student',
        'assignment'
    )

    # Leaves
    leaves = TeacherLeave.objects.filter(
        teacher=teacher
    )

    # Salary
    salary_data = calculate_teacher_salary(
        teacher
    )

    return render(
        request,
        'teachers/teacher_dashboard.html',
        {
            'teacher': teacher,
            'courses': courses,
            'students': students,
            'progress_list': progress_list,
            'assignments': assignments,
            'submissions': submissions,
            'leaves': leaves,
            'salary': salary_data,
        }
    )

# ---------------- Remove Student from Course ----------------
def remove_student_from_course(request, teacher_id, student_id, course_id):
    student = get_object_or_404(Student, id=student_id)
    course = get_object_or_404(Course, id=course_id)
    student.courses.remove(course)
    return redirect('teacher_dashboard')

#-----------------teacherprofile-------------------------
@login_required
def teacher_profile(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)

    if request.method == "POST":
        profile_pic = request.FILES.get('profile_pic')
        if profile_pic:
            teacher.profile_pic = profile_pic
            teacher.save()
        return redirect('teacher_profile', teacher_id=teacher.id)

    return render(request, 'teachers/teacher_profile.html', {
        'teacher': teacher,
        'courses': teacher.courses.all()
    })
#-----------------edit teacher profile-------------------------
@login_required
def edit_teacher_profile(request, teacher_id):
    teacher = Teacher.objects.get(id=teacher_id)
    courses = Course.objects.all()

    if request.method == "POST":
        teacher.name = request.POST.get("name")

        # update email
        teacher.user.email = request.POST.get("email")
        teacher.user.save()

        # salary fix
        salary = request.POST.get("salary")
        if salary:
            teacher.salary = float(salary)

        teacher.save() 

        phone = request.POST.get("phone")
        teacher.phone = phone
        teacher.save()

        # update courses (ManyToMany)
        course_ids = request.POST.getlist('courses')
        teacher.courses.set(course_ids)   #  IMPORTANT

        return redirect('teacher_dashboard')
    
    return render(request, 'teachers/edit_teacher_profile.html', {
        'teacher': teacher,
        'courses': courses
    })

#-----------------enroll student in course-------------------------
@login_required
def enroll_student(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    students = Student.objects.all()
    courses = teacher.courses.all()

    if request.method == "POST":
        student_id = request.POST.get('student')
        course_id = request.POST.get('course')

        student = get_object_or_404(Student, id=student_id)
        course = get_object_or_404(Course, id=course_id)

        # prevent duplicate
        if course not in student.courses.all():
            student.courses.add(course)

        return redirect('teacher_dashboard')

    return render(request, 'teachers/enroll_student.html', {
        'teacher': teacher,
        'students': students,
        'courses': courses
    })

#-----------------course progress-------------------------
@login_required
def course_progress(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)

    courses = teacher.courses.all()
    progress_data = []

    #  loop properly
    for course in courses:
        students = Student.objects.filter(courses=course)

        for student in students:
            progress_obj, created = CourseProgress.objects.get_or_create(
                student=student,
                course=course,
                defaults={'progress': 0}
            )

            progress_data.append({
                'student': student,
                'course': course,
                'progress': progress_obj.progress
            })

    return render(request, 'teachers/course_progress.html', {
        'teacher': teacher,
        'progress_data': progress_data
    })

@login_required
def update_progress(request, student_id, course_id, teacher_id):
    # Optional: restrict only teacher
    if not hasattr(request.user, 'teacher'):
        return redirect('home')

    student = get_object_or_404(Student, id=student_id)

    progress_obj, _ = CourseProgress.objects.get_or_create(
        student=student,
        course_id=course_id
    )

    progress_obj.progress += 10

    if progress_obj.progress > 100:
        progress_obj.progress = 100

    progress_obj.save()

    return redirect('teacher_dashboard')

@login_required
def remove_progress(request, student_id, course_id):
    if not hasattr(request.user, 'teacher'):
        return redirect('home')

    student = get_object_or_404(Student, id=student_id)

    progress_obj, _ = CourseProgress.objects.get_or_create(
        student=student,
        course_id=course_id
    )

    progress_obj.progress -= 10

    if progress_obj.progress < 0:
        progress_obj.progress = 0

    progress_obj.save()

    return redirect('teacher_dashboard')  

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages

from teachers.models import Teacher
from timetable.models import Timetable
from students.models import Attendance, Student
from notifications.models import Notification


@login_required
def mark_attendance(request):

    teacher = get_object_or_404(
        Teacher,
        user=request.user
    )

    today = timezone.localdate()

    current_day = today.strftime("%A")

    current_time = timezone.localtime().time()

    lecture = Timetable.objects.filter(
        teacher=teacher,
        day=current_day,
        start_time__lte=current_time,
        end_time__gte=current_time
    ).first()

    if lecture is None:

        return render(
            request,
            "attendance/mark_attendance.html",
            {
                "lecture": None,
                "students": [],
                "today": today,
            }
        )

    students = Student.objects.filter(
        courses=lecture.course
    )

    if request.method == "POST":

        for student in students:

            status = request.POST.get(
                f"status_{student.id}",
                "Absent"
            )

            Attendance.objects.update_or_create(
                student=student,
                lecture=lecture,
                course=lecture.course,
                date=today,
                defaults={
                    "status": status
                }
            )

            if status == "Absent":

                Notification.objects.create(
                    user=student.user,
                    title="Attendance Alert",
                    message=f"You were marked absent in {lecture.course.name}."
                )

        messages.success(
            request,
            "Attendance saved successfully."
        )

        return redirect("attendance_dashboard")

    return render(
        request,
        "attendance/mark_attendance.html",
        {
            "lecture": lecture,
            "students": students,
            "today": today,
        }
    )

@login_required
def attendance_dashboard(request):
    students = Student.objects.all()
    courses = Course.objects.all()

    student_id = request.GET.get('student')
    selected_date = request.GET.get('date')

    attendance_data = []

    present_count = 0
    absent_count = 0
    attendance_percentage = 0

    if student_id and selected_date:

        student = get_object_or_404(
            Student,
            id=student_id
        )

        records = Attendance.objects.filter(
            student=student,
            date=selected_date
        )

        for record in records:

            attendance_data.append({
                'course': record.course,
                'status': record.status,
                'date': record.date
            })

            if record.status == "Present":
                present_count += 1
            else:
                absent_count += 1

        total = present_count + absent_count

        if total > 0:
            attendance_percentage = round(
                (present_count / total) * 100,
                1
            )

    return render(
        request,
        'attendance/attendance_dashboard.html',
        {
            'students': students,
            'courses': courses,
            'attendance_data': attendance_data,
            'selected_date': selected_date,

            # Statistics
            'present_count': present_count,
            'absent_count': absent_count,
            'attendance_percentage': attendance_percentage,
        }
    )

@login_required
def get_students_by_course(request):
    course_id = request.GET.get('course_id')

    students = Student.objects.filter(courses__id=course_id)

    data = [
        {
            'id': s.id,
            'name': s.name
        }
        for s in students
    ]

    return JsonResponse({'students': data})

from datetime import datetime

@login_required
def monthly_attendance(request):

    month_input = request.GET.get('month')

    if not month_input:
        month_input = datetime.now().strftime('%Y-%m')

    year, month = month_input.split('-')

    data = []

    students = Student.objects.all()

    for student in students:

        records = Attendance.objects.filter(
            student=student,
            date__year=int(year),
            date__month=int(month)
        )

        total = records.count()

        present = records.filter(
            status="Present"
        ).count()

        percentage = (
            (present / total) * 100
            if total > 0 else 0
        )

        data.append({
            'student': student.name,
            'present': present,
            'total': total,
            'percentage': round(percentage, 2)
        })

    # ==========================
    # Dashboard Statistics
    # ==========================

    percentages = [
        d['percentage']
        for d in data
    ]

    avg_attendance = (
        round(sum(percentages) / len(percentages), 1)
        if percentages else 0
    )

    highest_attendance = (
        max(percentages)
        if percentages else 0
    )

    lowest_attendance = (
        min(percentages)
        if percentages else 0
    )

    labels = [d['student'] for d in data]
    percentages = [d['percentage'] for d in data]

    return render(
    request,
    'attendance/monthly.html',
    {
        'data': data,
        'month_input': month_input,
        'avg_attendance': avg_attendance,
        'highest_attendance': highest_attendance,
        'lowest_attendance': lowest_attendance,

        'labels': labels,
        'percentages': percentages,
    }
)

@login_required
def create_assignment(request, course_id):
    teacher = request.user.teacher
    course = get_object_or_404(Course, id=course_id)

    if course not in teacher.courses.all():
       return redirect('teacher_dashboard')

    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        due_date = request.POST.get('due_date')
        attachment=request.FILES.get('attachment')

        assignment = Assignment.objects.create(
            title=title,
            description=description,
            due_date=due_date,
            course=course,
            attachment=attachment
        )
        students = Student.objects.filter(
            courses=course
        )
        
        for student in students:
            Notification.objects.create(
                user=student.user,
                title="New Assignment",
                message=f"Assignment '{assignment.title}' is available."
            )

        return redirect('teacher_dashboard')

    return render(request, 'teachers/create_assignment.html', {
        'course': course
    })

def grade_submissions(request,assignment_id):
    assignment = get_object_or_404(Assignment,id=assignment_id)
    submissions = Submission.objects.filter(assignment=assignment)
    if request.method =="POST":
        for submission in submissions:
            grade = request.POST.get(f'grade_{submission.id}')
            if grade:
                submission.grade = grade
                submission.save()
                return redirect('teacher_dashboard')
            return render(request,'teachers/grade_submissions.html',{
                'assignment':assignment,
                'submissions':submissions
            })
@login_required
def grade_assignment(request, assignment_id):

    assignment = get_object_or_404(
        Assignment,
        id=assignment_id
    )

    submissions = Submission.objects.filter(
        assignment=assignment
    )

    if request.method == "POST":

        for submission in submissions:

            grade = request.POST.get(
                f"grade_{submission.id}"
            )

            if grade:

                grade = int(grade)

                # Send notification only if the grade is new or changed
                if submission.grade != grade:

                    submission.grade = grade
                    submission.save()

                    Notification.objects.create(
                        user=submission.student.user,
                        title="Assignment Graded",
                        message=(
                            f"Your assignment '{submission.assignment.title}' "
                            f"has been graded.\n"
                            f"Marks: {submission.grade}"
                        )
                    )

        return redirect(
            "teacher_submissions"
        )

    return render(
        request,
        "teachers/grade_assignment.html",
        {
            "assignment": assignment,
            "submissions": submissions,
        }
    )

def view_assignments(request,course_id):
    course = get_object_or_404(Course,id=course_id)
    assignments = Assignment.objects.filter(course=course)
    return render(request,'teachers/view_assignments.html',{
        'course':course,
        'assignments':assignments
    })

@login_required
def view_submissions(request, assignment_id):
    teacher = request.user.teacher

    assignment = get_object_or_404(Assignment, id=assignment_id)

    #  Security check
    if assignment.course.teacher != teacher:
        return redirect('teacher_dashboard')

    #  All students in course
    students = assignment.course.students.all()

    # Submissions
    submissions = Submission.objects.filter(
        assignment=assignment
    ).select_related('student')

    # Students who submitted
    submitted_students = submissions.values_list('student_id', flat=True)

    # Students who did NOT submit
    not_submitted_students = students.exclude(id__in=submitted_students)

    return render(request, 'teachers/view_submissions.html', {
        'assignment': assignment,
        'submissions': submissions,
        'not_submitted_students': not_submitted_students
    }) 

def view_grades(request,assignments_id):
    assignment = get_object_or_404(Assignment,id=assignments_id)
    submission=Submission.objects.filter(assignment=assignment)  
    return render(request,'teachers/view_grades.html',{
        'assignment':assignment,
        'submissions':submission
    })

def view_submission_details(request,submission_id):
    submission = get_object_or_404(Submission,id=submission_id)
    return render(request,'teachers/submission_details.html',{
        'submission':submission
    })

def view_assignment_details(request,assignments_id):
    assignment = get_object_or_404(Assignment,id=assignments_id)
    return render(request,'teachers/assignments_details.html',{
        'assignment':assignment
    })

def delete_assignment(request,assignment_id):
    assignment = get_object_or_404(Assignment,id=assignment_id)
    if request.method =="POST":
        assignment.delete()
        return redirect('teacher_dashboard')
    return render(request,'teachers/delete_assignment.html',{
        'assignment':assignment
    })

@login_required
def edit_assignment(request, assignment_id):

    assignment = get_object_or_404(
        Assignment,
        id=assignment_id
    )

    if request.method == "POST":

        assignment.title = request.POST.get(
            'title'
        )

        assignment.description = request.POST.get(
            'description'
        )

        assignment.due_date = request.POST.get(
            'due_date'
        )

        # update attachment
        if request.FILES.get('attachment'):

            assignment.attachment = request.FILES.get(
                'attachment'
            )

        assignment.save()

        messages.success(
            request,
            "Assignment updated successfully"
        )

        return redirect(
            'teacher_dashboard'
        )

    return render(
        request,
        'teachers/edit_assignment.html',
        {
            'assignment': assignment
        }
    )

@login_required
def delete_assignment(request, assignment_id):

    assignment = get_object_or_404(
        Assignment,
        id=assignment_id
    )

    assignment.delete()

    messages.success(
        request,
        "Assignment deleted successfully"
    )

    return redirect(
        'teacher_assignments'
    )

@login_required
def teacher_assignments(request):
    teacher = request.user.teacher

    courses = teacher.courses.all()
    assignments = Assignment.objects.filter(course__in=courses).select_related('course')

    return render(request, 'teachers/teacher_assignments.html', {
        'courses': courses,
        'assignments': assignments
    })

@login_required
def teacher_submissions(request):
    teacher = request.user.teacher

    courses = teacher.courses.all()

    submissions = Submission.objects.filter(
        assignment__course__in=courses
    ).select_related('student', 'assignment', 'assignment__course')

    return render(request, 'teachers/teacher_submissions.html', {
        'submissions': submissions
    })

@login_required
def teacher_progress(request):
    teacher = request.user.teacher

    courses = teacher.courses.all()

    progress_list = CourseProgress.objects.filter(
        course__in=courses
    ).select_related('student', 'course')

    return render(request, 'teachers/teacher_progress.html', {
        'progress_list': progress_list,
        'teacher': teacher
    })

from django.shortcuts import render, redirect
from .models import Teacher, TeacherLeave
from django.contrib.auth.decorators import login_required

@login_required
def apply_leave(request):
    teacher = Teacher.objects.get(user=request.user)  

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')

        TeacherLeave.objects.create(
            teacher=teacher,
            start_date=start_date,
            end_date=end_date,
            reason=reason
        )

        Notification.objects.create(
            message=f" {teacher.name} applied for leave"
        )

        return redirect('leave_dashboard')  

    return render(request, 'teachers/apply_leave.html') 
from .models import TeacherSalary
from django.utils.timezone import now
from django.utils.timezone import now

from .models import Teacher, TeacherSalary
from .services import calculate_teacher_salary
from django.utils.timezone import now

def save_teacher_salary(teacher, salary_data):
    current_month = now().date().replace(day=1)

    TeacherSalary.objects.update_or_create(
        teacher=teacher,
        month=current_month,
        defaults={
            'base_salary': salary_data["base_salary"],
            'total_leave_days': salary_data["total_leave_days"],
            'deduction': salary_data["deduction"],
            'final_salary': salary_data["final_salary"],
        }
    )

@login_required
def salary_dashboard(request):

    teacher = Teacher.objects.get(
        user=request.user
    )

    # Calculate current salary
    salary = calculate_teacher_salary(
        teacher
    )

    # Save current month salary
    save_teacher_salary(
        teacher,
        salary
    )

    # Salary history
    salaries = TeacherSalary.objects.filter(
        teacher=teacher
    ).order_by('-month')

    return render(
        request,
        'teachers/salary_dashboard.html',
        {
            'teacher': teacher,
            'salary': salary,
            'salaries': salaries,
        }
    )
 
@login_required
def leave_dashboard(request):
    teacher = Teacher.objects.get(user=request.user)

    leaves = TeacherLeave.objects.filter(
        teacher=teacher
    ).order_by('-applied_at')

    return render(
        request,
        'teachers/leave_dashboard.html',
        {
            'leaves': leaves
        }
    )