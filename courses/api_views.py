from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from django.contrib.auth.decorators import login_required

from .models import Course, Note, Assignment, Submission
from students.models import CourseProgress
from teachers.models import Teacher
from students.models import Student

from .serializers import (
    CourseSerializer,
    NoteSerializer,
    AssignmentSerializer,
    CourseProgressSerializer
)

# ===================== COURSE APIs =====================

class CourseAPI(APIView):

    def get(self, request):
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CourseDetailAPI(APIView):

    def get(self, request, pk):
        course = get_object_or_404(Course, id=pk)
        serializer = CourseSerializer(course)
        return Response(serializer.data)

    def put(self, request, pk):
        course = get_object_or_404(Course, id=pk)
        serializer = CourseSerializer(course, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        course = get_object_or_404(Course, id=pk)
        course.delete()
        return Response({"message": "Course deleted"})
# ===================== ENROLL / UNENROLL =====================

class EnrollAPI(APIView):

    def post(self, request, course_id):
        student = Student.objects.get(user=request.user)
        course = get_object_or_404(Course, id=course_id)

        student.courses.add(course)

        CourseProgress.objects.get_or_create(
            student=student,
            course=course,
            defaults={'progress': 0}
        )

        return Response({"message": "Enrolled successfully"})

class UnenrollAPI(APIView):

    def post(self, request, course_id):
        student = Student.objects.get(user=request.user)
        course = get_object_or_404(Course, id=course_id)

        student.courses.remove(course)

        return Response({"message": "Unenrolled successfully"})

# ===================== PROGRESS =====================

class ProgressAPI(APIView):

    def get(self, request, course_id):
        try:
            student = Student.objects.get(user=request.user)

            progress = CourseProgress.objects.get(
                student=student,
                course_id=course_id
            )

            serializer = CourseProgressSerializer(progress)
            return Response(serializer.data)

        except Student.DoesNotExist:
            return Response(
                {"error": "Student profile not found"},
                status=404
            )

        except CourseProgress.DoesNotExist:
            return Response(
                {"error": "Progress not found for this course"},
                status=404
            )

class UpdateProgressAPI(APIView):

    def post(self, request, course_id):
        student = Student.objects.get(user=request.user)

        progress, _ = CourseProgress.objects.get_or_create(
            student=student,
            course_id=course_id
        )

        progress.progress = min(progress.progress + 10, 100)
        progress.save()

        return Response({"progress": progress.progress})


# ===================== NOTES =====================

class NoteAPI(APIView):

    def get(self, request, course_id):
        notes = Note.objects.filter(course_id=course_id)
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data)

class AddNoteAPI(APIView):

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)

        note = Note.objects.create(
            course=course,
            title=request.data.get("title"),
            file=request.FILES.get("file")
        )

        return Response({"message": "Note created"})
    
# ===================== ASSIGNMENTS =====================

class AssignmentAPI(APIView):

    def get(self, request, course_id):
        assignments = Assignment.objects.filter(course_id=course_id)
        serializer = AssignmentSerializer(assignments, many=True)
        return Response(serializer.data)

class AssignmentCreateAPI(APIView):

    def post(self, request):
        serializer = AssignmentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  