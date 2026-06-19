from django import forms
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from courses.models import Course
from teachers.models import Teacher
from students.models import Student
from .models import Complaint
from .forms import ComplaintForm
from django.utils import timezone

@login_required
def create_complaint(request):

    student = Student.objects.get(
        user=request.user
    )

    if request.method == "POST":

        form = ComplaintForm(
            request.POST,
            request.FILES
        )

        # Only enrolled courses
        form.fields['course'].queryset = student.courses.all()

        if form.is_valid():

            complaint = form.save(
                commit=False
            )

            complaint.student = student

            category = complaint.category

            # ADMIN COMPLAINTS
            if category in [
                "Fees",
                "Technical",
                "Hostel",
                "Other"
            ]:

                admin = User.objects.filter(
                    is_superuser=True
                ).first()

                complaint.assigned_admin = admin

            # TEACHER COMPLAINTS
            elif category in [
                "Attendance",
                "Assignment",
                "Subject"
            ]:

                teacher = Teacher.objects.filter(
                    courses=complaint.course
                ).first()

                complaint.assigned_teacher = teacher

            complaint.save()

            return redirect(
                "my_complaints"
            )

    else:

        form = ComplaintForm()

        # Only show enrolled courses
        form.fields['course'].queryset = student.courses.all()

    return render(
        request,
        "complaints/create.html",
        {
            "form": form
        }
    )

from django.shortcuts import render, redirect, get_object_or_404
from .models import Complaint


def resolve_complaint(request, id):

    complaint = get_object_or_404(
        Complaint,
        id=id
    )

    if request.method == "POST":

        complaint.status = request.POST.get(
            "status"
        )

        complaint.reply = request.POST.get(
            "reply"
        )

        complaint.save()

        return redirect(
            request.META.get(
                "HTTP_REFERER",
                "/"
            )
        )

    return render(
        request,
        "complaints/resolve.html",
        {
            "complaint": complaint
        }
    )

@login_required
def my_complaints(request):


    student = Student.objects.get(
        user=request.user
    )


    data = Complaint.objects.filter(
        student=student
    )


    return render(
        request,
        "complaints/my.html",
        {
        "complaints":data
        }
    )

@login_required
def teacher_complaints(request):


    teacher = Teacher.objects.get(
        user=request.user
    )


    complaints = Complaint.objects.filter(
        assigned_teacher=teacher
    )


    return render(
    request,
    "complaints/complaints.html",
    {
      "complaints":complaints
    }
)

@login_required
def admin_complaints(request):


    complaints = Complaint.objects.filter(
        assigned_admin=request.user
    )


    return render(
        request,
        "complaints/complaints.html",
        {
        "complaints":complaints
        }
    )

from django.contrib import messages

@login_required
def resolve_complaint(request, id):

    complaint = get_object_or_404(
        Complaint,
        id=id
    )

    if request.method == "POST":

        complaint.status = request.POST.get(
            "status"
        )

        complaint.reply = request.POST.get(
            "reply"
        )

        if complaint.status == "Resolved":
            complaint.resolved_at = timezone.now()

        complaint.save()

        messages.success(
            request,
            "Complaint updated successfully."
        )

        if request.user.is_superuser:
            return redirect(
                "admin_complaints"
            )

        return redirect(
            "teacher_complaints"
        )

    return render(
        request,
        "complaints/resolve.html",
        {
            "complaint": complaint
        }
    )

class ComplaintForm(forms.ModelForm):

    class Meta:
        model = Complaint

        fields = [
            'course',
            'category',
            'priority',
            'title',
            'description',
            'attachment'
        ]

        widgets = {

            'course': forms.Select(
                attrs={'class': 'form-select'}
            ),

            'category': forms.Select(
                attrs={'class': 'form-select'}
            ),

            'priority': forms.Select(
                attrs={'class': 'form-select'}
            ),

            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter complaint title'
                }
            ),

            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 5,
                    'placeholder': 'Describe your issue'
                }
            ),
        }