from datetime import datetime

from django.shortcuts import get_object_or_404

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Timetable
from .serializers import TimetableSerializer
from students.models import Student
from teachers.models import Teacher


class TimetableViewSet(ModelViewSet):

    queryset = Timetable.objects.all().order_by("id")
    serializer_class = TimetableSerializer

    @action(detail=False)
    def student(self, request):

        student = get_object_or_404(Student, user=request.user)

        serializer = self.get_serializer(
            self.get_queryset().filter(course__in=student.courses.all()),
            many=True
        )

        return Response(serializer.data)
    
    @action(detail=False)
    def teacher(self, request):

        teacher = get_object_or_404(Teacher, user=request.user)

        serializer = self.get_serializer(
            self.get_queryset().filter(teacher=teacher),
            many=True
        )

        return Response(serializer.data)

    @action(detail=False, url_path=r"course/(?P<course_id>\d+)")
    def course(self, request, course_id=None):

        serializer = self.get_serializer(
            self.get_queryset().filter(course_id=course_id),
            many=True
        )

        return Response(serializer.data)

    @action(detail=False, url_path=r"day/(?P<day>[^/.]+)")
    def day(self, request, day=None):

        serializer = self.get_serializer(
            self.get_queryset().filter(day__iexact=day),
            many=True
        )

        return Response(serializer.data)

    @action(detail=False, url_path=r"teacher-id/(?P<teacher_id>\d+)")
    def teacher_by_id(self, request, teacher_id=None):

        serializer = self.get_serializer(
            self.get_queryset().filter(teacher_id=teacher_id),
            many=True
        )

        return Response(serializer.data)

    @action(detail=False, url_path=r"classroom/(?P<classroom>[^/.]+)")
    def classroom(self, request, classroom=None):

        serializer = self.get_serializer(
            self.get_queryset().filter(
                classroom__iexact=classroom
            ),
            many=True
        )

        return Response(serializer.data)
    
    @action(detail=False)
    def today(self, request):

        serializer = self.get_serializer(
            self.get_queryset().filter(
                day=datetime.today().strftime("%A")
            ),
            many=True
        )

        return Response(serializer.data)

    @action(detail=False)
    def search(self, request):

        serializer = self.get_serializer(
            self.get_queryset().filter(
                day__icontains=request.query_params.get("day", "")
            ),
            many=True
        )

        return Response(serializer.data)

    @action(detail=False)
    def statistics(self, request):

        queryset = self.get_queryset()

        return Response({
            "total_classes": queryset.count(),

            "total_courses": queryset.values(
                "course"
            ).distinct().count(),

            "total_teachers": queryset.values(
                "teacher"
            ).distinct().count(),

            "total_classrooms": queryset.values(
                "classroom"
            ).distinct().count(),
        })

    @action(detail=False)
    def count(self, request):

        return Response({
            "count": self.get_queryset().count()
        })