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
from students.models import Submission
from .models import Course, Note, Assignment
from .serializers import (
    CourseSerializer,
    NoteSerializer,
    AssignmentSerializer,
    CourseProgressSerializer
)

from students.models import Student, CourseProgress
from teachers.models import Teacher
from notifications.models import Notification


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

        CourseProgress.objects.filter(
            student=student,
            course=course
        ).delete()

        return Response(
            {
                "message":"Unenrolled successfully"
            }
        )
    
    @action(
    detail=True,
    methods=["delete"],
    url_path="remove-teacher/(?P<teacher_id>[^/.]+)"
    )
    def remove_teacher(self, request, pk=None, teacher_id=None):

        course = self.get_object()

        teacher = get_object_or_404(
            Teacher,
            id=teacher_id
        )

        teacher.courses.remove(course)

        return Response({
            "message":"Teacher removed successfully"
        })

    @action(
    detail=True,
    methods=["delete"],
    url_path="remove-student/(?P<student_id>[^/.]+)"
    )
    def remove_student(self, request, pk=None, student_id=None):

        course = self.get_object()

        student = get_object_or_404(
            Student,
            id=student_id
        )

        student.courses.remove(course)


        return Response({
            "message":"Student removed successfully"
        })

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
    
    @action(detail=True, methods=["post"])
    def teacher_update_progress(self,request,pk=None):

        course=self.get_object()

        teacher=self.get_teacher()

        if not teacher.courses.filter(id=course.id).exists():

            return Response(
                {
                    "error":"Not assigned"
                },
                status=403
            )


        for student in course.enrolled_students.all():

            progress,_=CourseProgress.objects.get_or_create(
                student=student,
                course=course
            )

            progress.progress=min(
                progress.progress+10,
                100
            )

            progress.save()


        return Response(
            {
                "message":"Progress updated"
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
    
    @action(detail=False, methods=["get"])
    def my_notes(self, request):

        student = self.get_student()

        notes = Note.objects.filter(
            course__in=student.courses.all()
        )

        serializer = NoteSerializer(
            notes,
            many=True
        )

        return Response(serializer.data)
    
    @action(detail=False, methods=["get"])
    def filter(self, request):

        queryset = self.get_queryset()

        duration = request.query_params.get("duration")
        min_fees = request.query_params.get("min_fees")

        if duration:
            queryset = queryset.filter(duration=duration)

        if min_fees:
            queryset = queryset.filter(fees__gte=min_fees)

        serializer = self.get_serializer(
            queryset,
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
    
    @action(
    detail=True,
    methods=["delete"],
    url_path="delete-note/(?P<note_id>[^/.]+)"
    )
    def delete_note(self, request, pk=None, note_id=None):

        self.get_teacher()

        course = self.get_object()

        note = get_object_or_404(
            Note,
            id=note_id,
            course=course
        )

        note.delete()

        return Response({
            "message": "Note deleted successfully"
        })
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

    @action(detail=False, methods=["get"])
    def my_progress(self, request):

        student = self.get_student()

        progress = CourseProgress.objects.filter(
            student=student
        )

        serializer = CourseProgressSerializer(
            progress,
            many=True
        )

        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def teachers(self, request, pk=None):

        course = self.get_object()

        from teachers.serializers import TeacherSerializer

        serializer = TeacherSerializer(
            course.assigned_teachers.all(),
            many=True
        )

        return Response(serializer.data)
    
    @action(detail=True, methods=["get"])
    def teacher_progress_dashboard(self, request, pk=None):

        course = self.get_object()

        return Response({

            "course": course.name,

            "teachers": [
                teacher.name
                for teacher in course.assigned_teachers.all()
            ],

            "students": CourseProgressSerializer(
                CourseProgress.objects.filter(course=course),
                many=True
            ).data

        })

# ====================================================
# ASSIGNMENT VIEWSET
# ====================================================

class AssignmentViewSet(ModelViewSet):

    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):

        assignment = serializer.save()

        students = Student.objects.filter(
            courses=assignment.course
        )

        for student in students:

            Notification.objects.create(

                user=student.user,

                title="New Assignment",

                message=f"{assignment.title} uploaded"

            )

    @action(
    detail=True,
    methods=["get"]
    )
    def detail(self, request, pk=None):

        assignment = self.get_object()

        submission = None

        if hasattr(request.user,'student'):

            submission = Submission.objects.filter(
                student=request.user.student,
                assignment=assignment
            ).first()

        return Response({

            "assignment":
            AssignmentSerializer(assignment).data,

            "submission":
            SubmissionSerializer(submission).data
            if submission else None

        })
    
    @action(detail=True, methods=["put"])
    def edit_assignment(self, request, pk=None):

        assignment = self.get_object()

        serializer = AssignmentSerializer(
            assignment,
            data=request.data
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                {
                    "message":"Assignment updated successfully",
                    "data":serializer.data
                }
            )
        
        return Response(
            serializer.errors,
            status=400
        )
    
    def destroy(self,request,*args,**kwargs):

        assignment=self.get_object()

        teacher=request.user.teacher

        if not teacher.courses.filter(
            id=assignment.course.id
        ).exists():

            return Response(
                {
                    "error":"You cannot delete this assignment"
                },
                status=403
            )

        assignment.delete()

        return Response(
            {
                "message":"Assignment deleted"
            }
        )
    
    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):

        assignment=self.get_object()

        student=get_object_or_404(
            Student,
            user=request.user
        )

        submission=Submission.objects.create(
            assignment=assignment,
            student=student,
            file=request.FILES.get("file")
        )

        return Response(
            {
                "message":"Assignment submitted",
                "id":submission.id
            },
            status=201
        )

    @action(detail=False, methods=["get"])
    def my_assignments(self,request):

        teacher=get_object_or_404(
            Teacher,
            user=request.user
        )

        assignments=Assignment.objects.filter(
            course__in=teacher.courses.all()
        )

        serializer=AssignmentSerializer(
            assignments,
            many=True
        )

        return Response(serializer.data)
    
# ====================================================
# NOTE VIEWSET
# ====================================================

class NoteViewSet(ModelViewSet):

    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]