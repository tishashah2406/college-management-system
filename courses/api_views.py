from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.utils import timezone

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

from rest_framework.permissions import IsAuthenticated
# ===================== COURSE VIEWSET =====================

class CourseViewSet(viewsets.ModelViewSet):

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    # ===================== ENROLL =====================

    @action(detail=True, methods=['post'])
    def enroll(self, request, pk=None):

        student = get_object_or_404(
            Student,
            user=request.user
        )

        course = self.get_object()

        if student.courses.filter(
            id=course.id
        ).exists():
            return Response({
                "message": "Already enrolled"
            })

        student.courses.add(course)

        CourseProgress.objects.get_or_create(
            student=student,
            course=course,
            defaults={'progress': 0}
        )

        return Response({
            "message": "Enrolled successfully"
        })
    # ===================== UNENROLL =====================

    @action(detail=True, methods=['post'])
    def unenroll(self, request, pk=None):

        student = get_object_or_404(
            Student,
            user=request.user
        )
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

        student = get_object_or_404(
            Student,
            user=request.user
        )

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
       
       if not Teacher.objects.filter(
            user=request.user
        ).exists():

            return Response(
                {"error": "Only teachers can add notes"},
                status=status.HTTP_403_FORBIDDEN
            )

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
    
    @action(detail=True, methods=["get"])
    def dashboard(self, request, pk=None):

        course = self.get_object()

        return Response({
            "course": CourseSerializer(course).data,
            "teacher": course.teacher.name if hasattr(course, "teacher") else None,
            "students": Student.objects.filter(courses=course).count(),
            "notes": Note.objects.filter(course=course).count(),
            "assignments": Assignment.objects.filter(course=course).count()
        })
    
    @action(detail=True, methods=["get"])
    def students(self, request, pk=None):

        course = self.get_object()

        students = Student.objects.filter(
            courses=course
        )

        from students.serializers import StudentSerializer

        serializer = StudentSerializer(
            students,
            many=True
        )

        return Response(serializer.data)
    
    @action(detail=False, methods=["get"])
    def search(self, request):

        keyword = request.query_params.get("q", "")

        courses = Course.objects.filter(
            name__icontains=keyword
        )

        serializer = CourseSerializer(
            courses,
            many=True
        )

        return Response(serializer.data)
    
    @action(detail=True, methods=["get"])
    def completion(self, request, pk=None):

        course = self.get_object()

        progress = CourseProgress.objects.filter(
            course=course
        )

        average = progress.aggregate(
            Avg("progress")
        )["progress__avg"] or 0

        return Response({
            "course": course.name,
            "completion": round(average, 2)
        })

    @action(detail=True, methods=["get"])
    def upcoming_assignments(self, request, pk=None):

        assignments = Assignment.objects.filter(
            course_id=pk,
            due_date__gte=timezone.now().date()
        ).order_by("due_date")

        serializer = AssignmentSerializer(
            assignments,
            many=True
        )

        return Response(serializer.data)
    
    @action(detail=True, methods=["get"])
    def expired_assignments(self, request, pk=None):

        assignments = Assignment.objects.filter(
            course_id=pk,
            due_date__lt=timezone.now().date()
        )

        serializer = AssignmentSerializer(
            assignments,
            many=True
        )

        return Response(serializer.data)
    
    @action(detail=True, methods=["get"])
    def submission_stats(self, request, pk=None):

        course = self.get_object()

        total = Assignment.objects.filter(
            course=course
        ).count()

        submitted = Submission.objects.filter(
            assignment__course=course
        ).count()

        return Response({

            "course": course.name,

            "total_assignments": total,

            "total_submissions": submitted
        })
    
    @action(detail=True, methods=["get"])
    def top_students(self, request, pk=None):

        course = self.get_object()

        data = []

        students = Student.objects.filter(
            courses=course
        )

        for student in students:

            avg = Submission.objects.filter(
                student=student,
                assignment__course=course
            ).aggregate(
                Avg("grade")
            )["grade__avg"] or 0

            data.append({
                "student": student.user.username,
                "average_grade": round(avg, 2)
            })

        data.sort(
            key=lambda x: x["average_grade"],
            reverse=True
        )

        return Response(data[:10])
    
    @action(detail=True, methods=["get"])
    def student_count(self, request, pk=None):

        course = self.get_object()

        return Response({
            "students": Student.objects.filter(
                courses=course
            ).count()
        })
    
    @action(detail=False, methods=["get"])
    def teacher_courses(self, request):

        teacher = get_object_or_404(
            Teacher,
            user=request.user
        )

        serializer = CourseSerializer(
            teacher.courses.all(),
            many=True
        )

        return Response(serializer.data)
    
    @action(detail=True, methods=["get"])
    def progress_list(self, request, pk=None):

        progress = CourseProgress.objects.filter(
            course_id=pk
        )

        serializer = CourseProgressSerializer(
            progress,
            many=True
        )

        return Response(serializer.data)
    
    @action(detail=True, methods=["get"])
    def notes_download(self, request, pk=None):

        notes = Note.objects.filter(
            course_id=pk
        )

        return Response([
            {
                "title": note.title,
                "file": note.file.url if note.file else None
            }
            for note in notes
        ])
    

# ===================== ASSIGNMENT VIEWSET =====================
class AssignmentViewSet(viewsets.ModelViewSet):

    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]

class NoteViewSet(viewsets.ModelViewSet):

    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]