from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

from .models import Timetable
from .serializers import TimetableSerializer

from students.models import Student
from teachers.models import Teacher

from datetime import datetime


class CreateTimetableAPIView(APIView):

    def post(self, request):

        serializer = TimetableSerializer(
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class TimetableListAPIView(APIView):

    def get(self, request):

        timetables = Timetable.objects.all()

        serializer = TimetableSerializer(
            timetables,
            many=True
        )

        return Response(serializer.data)

class StudentTimetableAPIView(APIView):

    def get(self, request):

        student = get_object_or_404(
            Student,
            user=request.user
        )

        timetables = Timetable.objects.filter(
            course__in=student.courses.all()
        )

        serializer = TimetableSerializer(
            timetables,
            many=True
        )

        return Response(serializer.data)

class TeacherTimetableAPIView(APIView):

    def get(self, request):

        teacher = get_object_or_404(
            Teacher,
            user=request.user
        )

        timetables = Timetable.objects.filter(
            teacher=teacher
        )

        serializer = TimetableSerializer(
            timetables,
            many=True
        )

        return Response(serializer.data)

class UpdateTimetableAPIView(APIView):

    def put(self, request, pk):

        timetable = get_object_or_404(
            Timetable,
            pk=pk
        )

        serializer = TimetableSerializer(
            timetable,
            data=request.data
        )

        if serializer.is_valid():

            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class DeleteTimetableAPIView(APIView):

    def delete(self, request, pk):

        timetable = get_object_or_404(
            Timetable,
            pk=pk
        )

        timetable.delete()

        return Response(
            {"message": "Deleted"},
            status=status.HTTP_204_NO_CONTENT
        )
    
class TimetableDetailAPIView(APIView):

    def get(self, request, pk):

        timetable = get_object_or_404(
            Timetable,
            pk=pk
        )

        serializer = TimetableSerializer(
            timetable
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
    
class PartialUpdateTimetableAPIView(APIView):

    def patch(self, request, pk):

        timetable = get_object_or_404(
            Timetable,
            pk=pk
        )

        serializer = TimetableSerializer(
            timetable,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
class CourseTimetableAPIView(APIView):

    def get(self, request, course_id):

        timetables = Timetable.objects.filter(
            course_id=course_id
        )

        serializer = TimetableSerializer(
            timetables,
            many=True
        )

        return Response(serializer.data)

class DayTimetableAPIView(APIView):

    def get(self, request, day):

        timetables = Timetable.objects.filter(
            day__iexact=day
        )

        serializer = TimetableSerializer(
            timetables,
            many=True
        )

        return Response(serializer.data)
    
class TeacherTimetableByIdAPIView(APIView):

    def get(self, request, teacher_id):

        timetables = Timetable.objects.filter(
            teacher_id=teacher_id
        )

        serializer = TimetableSerializer(
            timetables,
            many=True
        )

        return Response(serializer.data)
    
class RoomTimetableAPIView(APIView):

    def get(self, request, room):

        timetables = Timetable.objects.filter(
            room__iexact=room
        )

        serializer = TimetableSerializer(
            timetables,
            many=True
        )

        return Response(serializer.data)
    
class TodayTimetableAPIView(APIView):

    def get(self, request):

        today = datetime.today().strftime("%A")

        timetables = Timetable.objects.filter(
            day=today
        )

        serializer = TimetableSerializer(
            timetables,
            many=True
        )

        return Response(serializer.data)
    
class SearchTimetableAPIView(APIView):

    def get(self, request):

        day = request.query_params.get("day")

        timetables = Timetable.objects.filter(
            day__icontains=day
        )

        serializer = TimetableSerializer(
            timetables,
            many=True
        )

        return Response(serializer.data)
    
class TimetableStatisticsAPIView(APIView):

    def get(self, request):

        timetables = Timetable.objects.all()

        total_classes = timetables.count()

        total_courses = timetables.values(
            "course"
        ).distinct().count()

        total_teachers = timetables.values(
            "teacher"
        ).distinct().count()

        total_classrooms = timetables.values(
            "classroom"
        ).distinct().count()

        return Response(
            {
                "total_classes": total_classes,
                "total_courses": total_courses,
                "total_teachers": total_teachers,
                "total_rooms": total_classrooms,
            },
            status=status.HTTP_200_OK
        )
    
class TimetableCountAPIView(APIView):

    def get(self, request):

        return Response(
            {
                "count": Timetable.objects.count()
            },
            status=status.HTTP_200_OK
        )