from django import forms
from .models import Timetable


class TimetableForm(forms.ModelForm):

    class Meta:
        model = Timetable

        fields = [
            "day",
            "course",
            "teacher",
            "classroom",
            "start_time",
            "end_time",
        ]

        widgets = {

            "day": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "course": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "teacher": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "classroom": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Classroom"
                }
            ),

            "start_time": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time"
                }
            ),

            "end_time": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time"
                }
            ),
        }

    def clean(self):

        cleaned_data = super().clean()

        teacher = cleaned_data.get("teacher")
        classroom = cleaned_data.get("classroom")
        day = cleaned_data.get("day")
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        # Start time should be before end time
        if start_time and end_time:
            if start_time >= end_time:
                raise forms.ValidationError(
                    "Start time must be earlier than end time."
                )

        # Teacher conflict
        if teacher and day and start_time and end_time:

            teacher_conflict = Timetable.objects.filter(
                teacher=teacher,
                day=day,
                start_time__lt=end_time,
                end_time__gt=start_time,
            )

            # Ignore current object while editing
            if self.instance.pk:
                teacher_conflict = teacher_conflict.exclude(
                    pk=self.instance.pk
                )

            if teacher_conflict.exists():
                raise forms.ValidationError(
                    "This teacher already has another lecture during this time."
                )

        # Classroom conflict
        if classroom and day and start_time and end_time:

            classroom_conflict = Timetable.objects.filter(
                classroom=classroom,
                day=day,
                start_time__lt=end_time,
                end_time__gt=start_time,
            )

            if self.instance.pk:
                classroom_conflict = classroom_conflict.exclude(
                    pk=self.instance.pk
                )

            if classroom_conflict.exists():
                raise forms.ValidationError(
                    "This classroom is already booked during this time."
                )

        return cleaned_data