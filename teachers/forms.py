from django import forms
from .models import Teacher
from courses.models import Course

class TeacherForm(forms.ModelForm):
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Teacher
        fields = ['name', 'email', 'salary', 'courses']