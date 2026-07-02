from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

from .models import Timetable
from .serializers import TimetableSerializer

from students.models import Student
from teachers.models import Teacher


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