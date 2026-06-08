from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from .models import Course, Note, Assignment, Submission
from students.models import CourseProgress, Student
from teachers.models import Teacher
from django.db.models import Avg
from .serializers import (
    CourseSerializer,
    NoteSerializer,
    AssignmentSerializer,
    CourseProgressSerializer,
    SubmissionSerializer
)

# ===================== COURSE VIEWSET =====================

class CourseViewSet(viewsets.ModelViewSet):

    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    # ===================== ENROLL =====================

    @action(detail=True, methods=['post'])
    def enroll(self, request, pk=None):

        student = Student.objects.get(user=request.user)
        course = self.get_object()

        student.courses.add(course)

        CourseProgress.objects.get_or_create(
            student=student,
            course=course,
            defaults={'progress': 0}
        )

        return Response({"message": "Enrolled successfully"})
    # ===================== UNENROLL =====================

    @action(detail=True, methods=['post'])
    def unenroll(self, request, pk=None):

        student = Student.objects.get(user=request.user)
        course = self.get_object()

        student.courses.remove(course)

        return Response({"message": "Unenrolled successfully"})
    
    # ===================== GET PROGRESS =====================

    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):

        try:
            student = Student.objects.get(user=request.user)

            progress = CourseProgress.objects.get(
                student=student,
                course_id=pk
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
                {"error": "Progress not found"},
                status=404
            )
        
    # ===================== UPDATE PROGRESS =====================

    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):

        student = Student.objects.get(user=request.user)

        progress, _ = CourseProgress.objects.get_or_create(
            student=student,
            course_id=pk
        )

        progress.progress = min(progress.progress + 10, 100)
        progress.save()

        return Response({
            "progress": progress.progress
        })

    # ===================== NOTES =====================

    @method_decorator(cache_page(60 * 10))
    @action(detail=True, methods=['get'])
    def notes(self, request, pk=None):

        notes = Note.objects.filter(course_id=pk)

        serializer = NoteSerializer(notes, many=True)

        return Response(serializer.data)

    # ===================== ADDNOTE =====================

    @action(detail=True, methods=['post'])
    def add_note(self, request, pk=None):

       course = self.get_object()

       title = request.data.get("title")
       file = request.FILES.get("file")

       if not title:
          return Response(
            {"error": "Title is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

       note = Note.objects.create(
        course=course,
        title=title,
        file=file
    )

       return Response({
        "message": "Note created"
    })

    # ===================== ASSIGNMENTS =====================

    @action(detail=True, methods=['get'])
    def assignments(self, request, pk=None):

        assignments = Assignment.objects.filter(course_id=pk)

        serializer = AssignmentSerializer(
            assignments,
            many=True
        )

        return Response(serializer.data)
    
    # ===================== MY COURSES =====================

    @action(detail=False, methods=['get'])
    def my_courses(self, request):

        student = Student.objects.filter(
            user=request.user
        ).first()

        if not student:
            return Response(
                {"error": "Student profile not found"},
                status=404
            )

        courses = student.courses.all()

        serializer = self.get_serializer(
            courses,
            many=True
        )

        return Response(serializer.data)

    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):

        course = self.get_object()

        total_students = Student.objects.filter(
            courses=course
        ).count()

        total_assignments = Assignment.objects.filter(
            course=course
        ).count()

        total_submissions = Submission.objects.filter(
            assignment__course=course
        ).count()

        average_progress = CourseProgress.objects.filter(
            course=course
        ).aggregate(
            Avg("progress")
        )["progress__avg"] or 0

        return Response({

            "course":
                course.name,

            "total_students":
                total_students,

            "total_assignments":
                total_assignments,

            "total_submissions":
                total_submissions,

            "average_progress":
                round(average_progress, 2)
        })
    
# ===================== ASSIGNMENT VIEWSET =====================
class AssignmentViewSet(viewsets.ModelViewSet):

    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer

class NoteViewSet(viewsets.ModelViewSet):

    queryset = Note.objects.all()
    serializer_class = NoteSerializer