from rest_framework import serializers

from .models import Timetable


class TimetableSerializer(serializers.ModelSerializer):

    class Meta:
        model = Timetable
        fields = "__all__"

    def validate(self, data):

        teacher = data["teacher"]
        classroom = data["classroom"]
        day = data["day"]
        start_time = data["start_time"]
        end_time = data["end_time"]

        # Start time must be before end time
        if start_time >= end_time:
            raise serializers.ValidationError({
                "start_time": "Start time must be before end time."
            })

        # Teacher conflict
        teacher_exists = Timetable.objects.filter(
            teacher=teacher,
            day=day,
            start_time__lt=end_time,
            end_time__gt=start_time
        )

        # Ignore current object while updating
        if self.instance:
            teacher_exists = teacher_exists.exclude(pk=self.instance.pk)

        if teacher_exists.exists():
            raise serializers.ValidationError({
                "teacher": "Teacher already has another lecture during this time."
            })

        # Classroom conflict
        classroom_exists = Timetable.objects.filter(
            classroom=classroom,
            day=day,
            start_time__lt=end_time,
            end_time__gt=start_time
        )

        if self.instance:
            classroom_exists = classroom_exists.exclude(pk=self.instance.pk)

        if classroom_exists.exists():
            raise serializers.ValidationError({
                "classroom": "Classroom is already occupied during this time."
            })

        return data