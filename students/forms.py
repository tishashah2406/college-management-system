from django import forms
from .models import Student
from courses.models import Course, Submission

class StudentForm(forms.ModelForm):
    # Optional: make courses a multi-select with checkboxes
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Student
        fields = ['name', 'email', 'age', 'courses']

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['file']

