from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.utils import timezone
from django.db.models import Avg

from .models import Course, Note, Assignment, Submission
from .serializers import (
    CourseSerializer,
    NoteSerializer,
    AssignmentSerializer,
    CourseProgressSerializer,
    SubmissionSerializer,
)

from students.models import Student, CourseProgress
from teachers.models import Teacher


class CourseViewSet(ModelViewSet):

    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Course.objects.all()

    # ------------------------
    # Helper Methods
    # ------------------------

    def get_student(self):
        return get_object_or_404(
            Student,
            user=self.request.user
        )

    def get_teacher(self):
        return get_object_or_404(
            Teacher,
            user=self.request.user
        )

    # ------------------------
    # ENROLL COURSE
    # ------------------------

    @action(detail=True, methods=["post"])
    def enroll(self, request, pk=None):

        student = self.get_student()
        course = self.get_object()

        if student.courses.filter(id=course.id).exists():

            return Response(
                {
                    "message": "Already enrolled"
                }
            )

        student.courses.add(course)

        CourseProgress.objects.get_or_create(
            student=student,
            course=course,
            defaults={
                "progress": 0
            }
        )

        return Response(
            {
                "message": "Enrolled successfully"
            }
        )

    # ------------------------
    # UNENROLL
    # ------------------------

    @action(detail=True, methods=["post"])
    def unenroll(self, request, pk=None):

        student = self.get_student()
        course = self.get_object()

        student.courses.remove(course)

        return Response(
            {
                "message": "Unenrolled successfully"
            }
        )

    # ------------------------
    # COURSE PROGRESS
    # ------------------------

    @action(detail=True, methods=["get"])
    def progress(self, request, pk=None):

        student = self.get_student()

        progress = get_object_or_404(
            CourseProgress,
            student=student,
            course=self.get_object()
        )

        serializer = CourseProgressSerializer(progress)

        return Response(serializer.data)
    
    # ------------------------
    # UPDATE PROGRESS
    # ------------------------

    @action(detail=True, methods=["post"])
    def update_progress(self, request, pk=None):

        student = self.get_student()

        progress, _ = CourseProgress.objects.get_or_create(
            student=student,
            course=self.get_object(),
            defaults={
                "progress": 0
            }
        )

        progress.progress = min(
            progress.progress + 10,
            100
        )

        progress.save()

        return Response(
            {
                "progress": progress.progress
            }
        )

    # ------------------------
    # COURSE NOTES
    # ------------------------

    @method_decorator(cache_page(60 * 10))
    @action(detail=True, methods=["get"])
    def notes(self, request, pk=None):

        serializer = NoteSerializer(
            Note.objects.filter(
                course=self.get_object()
            ),
            many=True
        )

        return Response(serializer.data)

    # ------------------------
    # ADD NOTE
    # ------------------------

    @action(detail=True, methods=["post"])
    def add_note(self, request, pk=None):

        self.get_teacher()

        title = request.data.get("title")

        if not title:

            return Response(
                {
                    "error": "Title is required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        Note.objects.create(

            course=self.get_object(),

            title=title,

            file=request.FILES.get("file")

        )

        return Response(
            {
                "message": "Note created successfully"
            },
            status=status.HTTP_201_CREATED
        )

    # ------------------------
    # ASSIGNMENTS
    # ------------------------

    @action(detail=True, methods=["get"])
    def assignments(self, request, pk=None):

        serializer = AssignmentSerializer(
            Assignment.objects.filter(
                course=self.get_object()
            ),
            many=True
        )

        return Response(serializer.data)

    # ------------------------
    # MY COURSES
    # ------------------------

    @action(detail=False, methods=["get"])
    def my_courses(self, request):

        serializer = self.get_serializer(
            self.get_student().courses.all(),
            many=True
        )

        return Response(serializer.data)

        # ------------------------
    # ANALYTICS
    # ------------------------

    @action(detail=True, methods=["get"])
    def analytics(self, request, pk=None):

        course = self.get_object()

        return Response({

            "course": course.name,

            "total_students": Student.objects.filter(
                courses=course
            ).count(),

            "total_assignments": Assignment.objects.filter(
                course=course
            ).count(),

            "total_submissions": Submission.objects.filter(
                assignment__course=course
            ).count(),

            "average_progress": round(

                CourseProgress.objects.filter(
                    course=course
                ).aggregate(
                    Avg("progress")
                )["progress__avg"] or 0,

                2
            )

        })

    # ------------------------
    # DASHBOARD
    # ------------------------

    @action(detail=True, methods=["get"])
    def dashboard(self, request, pk=None):

        course = self.get_object()

        return Response({

            "course": self.get_serializer(course).data,

            "teacher": getattr(
                getattr(course, "teacher", None),
                "name",
                None
            ),

            "students": Student.objects.filter(
                courses=course
            ).count(),

            "notes": Note.objects.filter(
                course=course
            ).count(),

            "assignments": Assignment.objects.filter(
                course=course
            ).count()

        })

    # ------------------------
    # COURSE STUDENTS
    # ------------------------

    @action(detail=True, methods=["get"])
    def students(self, request, pk=None):

        from students.serializers import StudentSerializer

        serializer = StudentSerializer(

            Student.objects.filter(
                courses=self.get_object()
            ),

            many=True

        )

        return Response(serializer.data)

    # ------------------------
    # SEARCH COURSES
    # ------------------------

    @action(detail=False, methods=["get"])
    def search(self, request):

        keyword = request.query_params.get("q", "")

        serializer = self.get_serializer(

            self.get_queryset().filter(
                name__icontains=keyword
            ),

            many=True

        )

        return Response(serializer.data)

    # ------------------------
    # COMPLETION %
    # ------------------------

    @action(detail=True, methods=["get"])
    def completion(self, request, pk=None):

        course = self.get_object()

        average = CourseProgress.objects.filter(

            course=course

        ).aggregate(

            Avg("progress")

        )["progress__avg"] or 0

        return Response({

            "course": course.name,

            "completion": round(
                average,
                2
            )

        })

    # ------------------------
    # UPCOMING ASSIGNMENTS
    # ------------------------

    @action(detail=True, methods=["get"])
    def upcoming_assignments(self, request, pk=None):

        serializer = AssignmentSerializer(

            Assignment.objects.filter(

                course=self.get_object(),

                due_date__gte=timezone.now().date()

            ).order_by("due_date"),

            many=True

        )

        return Response(serializer.data)

    # ------------------------
    # EXPIRED ASSIGNMENTS
    # ------------------------

    @action(detail=True, methods=["get"])
    def expired_assignments(self, request, pk=None):

        serializer = AssignmentSerializer(

            Assignment.objects.filter(

                course=self.get_object(),

                due_date__lt=timezone.now().date()

            ),

            many=True

        )

        return Response(serializer.data)

    # ------------------------
    # SUBMISSION STATS
    # ------------------------

    @action(detail=True, methods=["get"])
    def submission_stats(self, request, pk=None):

        course = self.get_object()

        return Response({

            "course": course.name,

            "total_assignments": Assignment.objects.filter(
                course=course
            ).count(),

            "total_submissions": Submission.objects.filter(
                assignment__course=course
            ).count()

        })

    # ------------------------
    # TOP STUDENTS
    # ------------------------

    @action(detail=True, methods=["get"])
    def top_students(self, request, pk=None):

        course = self.get_object()

        result = []

        for student in Student.objects.filter(courses=course):

            average = Submission.objects.filter(

                student=student,

                assignment__course=course

            ).aggregate(

                Avg("grade")

            )["grade__avg"] or 0

            result.append({

                "student": student.user.username,

                "average_grade": round(
                    average,
                    2
                )

            })

        result.sort(

            key=lambda x: x["average_grade"],

            reverse=True

        )

        return Response(result[:10])

    # ------------------------
    # STUDENT COUNT
    # ------------------------

    @action(detail=True, methods=["get"])
    def student_count(self, request, pk=None):

        return Response({
            "students": Student.objects.filter(
                courses=self.get_object()
            ).count()
        })

    # ------------------------
    # TEACHER COURSES
    # ------------------------

    @action(detail=False, methods=["get"])
    def teacher_courses(self, request):

        serializer = self.get_serializer(
            self.get_teacher().courses.all(),
            many=True
        )

        return Response(serializer.data)

    # ------------------------
    # PROGRESS LIST
    # ------------------------

    @action(detail=True, methods=["get"])
    def progress_list(self, request, pk=None):

        serializer = CourseProgressSerializer(
            CourseProgress.objects.filter(
                course=self.get_object()
            ),
            many=True
        )

        return Response(serializer.data)

    # ------------------------
    # NOTES DOWNLOAD
    # ------------------------

    @action(detail=True, methods=["get"])
    def notes_download(self, request, pk=None):

        notes = Note.objects.filter(
            course=self.get_object()
        )

        return Response([
            {
                "title": note.title,
                "file": note.file.url if note.file else None
            }
            for note in notes
        ])
    
# ====================================================
# ASSIGNMENT VIEWSET
# ====================================================

class AssignmentViewSet(ModelViewSet):

    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]


# ====================================================
# NOTE VIEWSET
# ====================================================

class NoteViewSet(ModelViewSet):

    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]