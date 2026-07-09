from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.db.models import Avg
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.views.decorators.cache import cache_page

from django.views.decorators.vary import vary_on_headers
from teachers.models import Teacher

from .models import Student, CourseProgress, Submission
from courses.models import Assignment
from .models import Student
from .serializers import StudentSerializer
from courses.serializers import (
    AssignmentSerializer,
    CourseProgressSerializer,
    CourseSerializer,
    SubmissionSerializer
)

class StudentViewSet(ModelViewSet):

    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        if self.request.user.is_superuser:
            return Student.objects.all()

        if Teacher.objects.filter(
            user=self.request.user
        ).exists():
            return Student.objects.all()

        return Student.objects.filter(
            user=self.request.user
        )   
    # ================ LOGGED-IN DASHBOARD =================
    @method_decorator(cache_page(60 * 5))
    @method_decorator(vary_on_headers("Authorization"))
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def dashboard(self, request):

        student = get_object_or_404(
            Student,
            user=request.user
        )

        courses = student.courses.prefetch_related(
            "assignments"
        )

        return Response({
            "student": StudentSerializer(student).data,
            "courses": CourseSerializer(courses, many=True).data,
            "progress": CourseProgressSerializer(
                CourseProgress.objects.filter(student=student),
                many=True
            ).data,
            "assignments": AssignmentSerializer(
                Assignment.objects.filter(course__in=courses),
                many=True
            ).data,
            "submissions": SubmissionSerializer(
                Submission.objects.filter(student=student),
                many=True
            ).data,
        })

    # ================= DASHBOARD BY ID =================
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated], url_path="dashboard-by-id")
    def dashboard_by_id(self, request, pk=None):

        if not request.user.is_superuser and not Teacher.objects.filter(
            user=request.user
        ).exists():

            return Response(
                {"error": "Permission denied"},
                status=403
            )

        student = get_object_or_404(Student, id=pk)
        courses = student.courses.all()

        return Response({
            "student": StudentSerializer(student).data,
            "courses": CourseSerializer(courses, many=True).data,
            "progress": CourseProgressSerializer(
                CourseProgress.objects.filter(student=student),
                many=True
            ).data,
            "assignments": AssignmentSerializer(
                Assignment.objects.filter(course__in=courses),
                many=True
            ).data,
            "submissions": SubmissionSerializer(
                Submission.objects.filter(student=student),
                many=True
            ).data,
        })

    # ================= SUBMIT ASSIGNMENT =================
    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def submit_assignment(self, request):

        assignment_id = request.data.get("assignment_id")

        # Only students can submit
        student = get_object_or_404(
            Student,
            user=request.user
        )

        assignment = get_object_or_404(
            Assignment,
            id=assignment_id
        )

        file = request.FILES.get("file")

        if not file:
            return Response(
                {"error": "File is required"},
                status=400
            )

        # Check enrollment
        if not student.courses.filter(
            id=assignment.course.id
        ).exists():

            return Response(
                {"error": "Not enrolled in this course"},
                status=403
            )

        # Create or update submission
        submission, created = Submission.objects.update_or_create(
            student=student,
            assignment=assignment,
            defaults={
                "file": file,
                "submitted_at": now()
            }
        )

        # Late submission check
        is_late = (
            assignment.due_date and
            submission.submitted_at.date() > assignment.due_date
        )

        # Clear cache
        cache.delete(f"student_dashboard_{student.id}")
        cache.delete(f"student_analytics_{student.id}")

        return Response({

            "message": (
                "Assignment submitted successfully"
                if created
                else "Assignment updated successfully"
            ),

            "created": created,

            "is_late": is_late,

            "submission": SubmissionSerializer(
                submission
            ).data
        })
        
    #assignment_progress
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def progress_report(self,request):
        student = get_object_or_404(
            Student,
            user=request.user
        )
        data=[]

        for course in student.courses.all():

            total_assignments = Assignment.objects.filter(course=course).count()

            completed_assignments = Submission.objects.filter(student=student,assignment__course=course).count()

            progress = 0

            if total_assignments > 0:
                progress=(completed_assignments/total_assignments)*100

            data.append({
                "course_id":course.id,
                "course_name":course.name,
                "total_assignments":total_assignments,
                "completed_assignments":completed_assignments,
                "progress_percentage":round(progress,2)
            })

        return Response(data)
    
    @method_decorator(cache_page(60 * 10))
    @method_decorator(vary_on_headers("Authorization"))   
    @action(detail=False,methods=['get'],permission_classes=[IsAuthenticated])
    def student_analytics(self, request):

        student = get_object_or_404(
            Student,
            user=request.user
        )
        courses_data = []

        total_assignments_all = 0
        total_completed_all = 0
        total_pending_all = 0
        total_late_submissions = 0

        # ================= COURSE LOOP =================
        for course in student.courses.all():

            # total assignments
            total_assignments = Assignment.objects.filter(
                course=course
            ).count()

            # completed assignments
            completed_assignments = Submission.objects.filter(
                student=student,
                assignment__course=course
            ).count()

            # pending assignments
            pending_assignments = (
                total_assignments - completed_assignments
            )

            # progress percentage
            progress = 0

            if total_assignments > 0:
                progress = (
                    completed_assignments / total_assignments
                ) * 100

            # course completed status
            is_completed = progress == 100

            # late submissions
            late_submissions = 0

            submissions = Submission.objects.filter(
                student=student,
                assignment__course=course
            )

            for submission in submissions:

                if (
                    submission.assignment.due_date and
                    submission.submitted_at.date() >
                    submission.assignment.due_date
                ):
                    late_submissions += 1

            total_late_submissions += late_submissions

            # pending assignment list
            submitted_assignment_ids = submissions.values_list(
                "assignment_id",
                flat=True
            )

            pending_assignment_list = Assignment.objects.filter(
                course=course
            ).exclude(
                id__in=submitted_assignment_ids
            )

            pending_assignment_names = [
                assignment.title
                for assignment in pending_assignment_list
            ]

            # add totals
            total_assignments_all += total_assignments
            total_completed_all += completed_assignments
            total_pending_all += pending_assignments

            # add course data
            courses_data.append({

                "course_id": course.id,

                "course_name": course.name,

                "total_assignments":
                    total_assignments,

                "completed_assignments":
                    completed_assignments,

                "pending_assignments":
                    pending_assignments,

                "pending_assignment_list":
                    pending_assignment_names,

                "late_submission_count":
                    late_submissions,

                "progress_percentage":
                    round(progress, 2),

                "is_completed":
                    is_completed
            })

        # ================= OVERALL PROGRESS =================
        overall_progress = 0

        if total_assignments_all > 0:
            overall_progress = (
                total_completed_all / total_assignments_all
            ) * 100

        # ================= LEADERBOARD =================
        leaderboard = []

        students = Student.objects.all()

        for s in students:

            total_assignments = Assignment.objects.filter(
                course__in=s.courses.all()
            ).count()

            completed_assignments = Submission.objects.filter(
                student=s
            ).count()

            progress = 0

            if total_assignments > 0:
                progress = (
                    completed_assignments / total_assignments
                ) * 100

            # average grade
            avg_grade = Submission.objects.filter(
                student=s
            ).aggregate(
                Avg("grade") # type: ignore
            )["grade__avg"] or 0

            # final score
            final_score = (
                progress * 0.7
            ) + (
                avg_grade * 0.3
            )

            leaderboard.append({

                "student_id": s.id,

                "student_name":
                    s.user.username,

                "progress":
                    round(progress, 2),

                "average_grade":
                    round(avg_grade, 2),

                "score":
                    round(final_score, 2)
            })

        # sort leaderboard
        leaderboard = sorted(
            leaderboard,
            key=lambda x: x["score"],
            reverse=True
        )

        # rank
        student_rank = None

        for index, item in enumerate(leaderboard, start=1):

            if item["student_id"] == student.id:
                student_rank = index
                break

        # ================= DASHBOARD CARDS =================
        dashboard_cards = {

            "total_courses":
                student.courses.count(),

            "total_assignments":
                total_assignments_all,

            "completed_assignments":
                total_completed_all,

            "pending_assignments":
                total_pending_all,

            "late_submissions":
                total_late_submissions,

            "overall_progress":
                round(overall_progress, 2)
        }

        # ================= FINAL RESPONSE =================
        return Response({

            "student_name":
                student.user.username,

            "student_rank":
                student_rank,

            "dashboard_cards":
                dashboard_cards,

            "courses":
                courses_data,

            "leaderboard":
                leaderboard[:10]
        })
    
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def profile(self, request):

        student = get_object_or_404(
            Student,
            user=request.user
        )

        serializer = StudentSerializer(student)
                                                                                  
        return Response(serializer.data)

    @action(detail=False, methods=["patch"], permission_classes=[IsAuthenticated])
    def update_profile(self, request):

        student = get_object_or_404(
            Student,
            user=request.user
        )

        serializer = StudentSerializer(
            student,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)
    
    @action(detail=False, methods=["get"])
    def my_courses(self, request):

        student = get_object_or_404(
            Student,
            user=request.user
        )

        serializer = CourseSerializer(
            student.courses.all(),
            many=True
        )

        return Response(serializer.data)
    
    @action(detail=False, methods=["get"])
    def pending_assignments(self, request):

        student = get_object_or_404(
            Student,
            user=request.user
        )

        submitted = Submission.objects.filter(
            student=student
        ).values_list(
            "assignment_id",
            flat=True
        )

        assignments = Assignment.objects.filter(
            course__in=student.courses.all()
        ).exclude(
            id__in=submitted
        )

        serializer = AssignmentSerializer(
            assignments,
            many=True
        )

        return Response(serializer.data)
    
    @action(detail=False, methods=["get"])
    def submitted_assignments(self, request):

        student = get_object_or_404(
            Student,
            user=request.user
        )

        serializer = SubmissionSerializer(
            Submission.objects.filter(student=student),
            many=True
        )

        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="course-progress")
    def course_progress(self, request, pk=None):

        student = get_object_or_404(
            Student,
            user=request.user
        )

        course = get_object_or_404(
            student.courses,
            id=pk
        )

        total = Assignment.objects.filter(
            course=course
        ).count()

        completed = Submission.objects.filter(
            student=student,
            assignment__course=course
        ).count()

        return Response({

            "course": course.name,

            "total": total,

            "completed": completed,

            "progress": round(
                completed * 100 / total if total else 0,
            )
        })
    
    @action(detail=False, methods=["get"])
    def assignment_history(self, request):

        student = get_object_or_404(
            Student,
            user=request.user
        )

        submissions = Submission.objects.filter(
            student=student
        ).order_by("-submitted_at")

        serializer = SubmissionSerializer(
            submissions,
            many=True
        )

        return Response(serializer.data)
    
    @action(detail=False, methods=["get"])
    def average_grade(self, request):

        student = get_object_or_404(
            Student,
            user=request.user
        )

        avg = Submission.objects.filter(
            student=student
        ).aggregate(
            Avg("grade")
        )

        return Response({
            "average_grade": avg["grade__avg"] or 0
        })

    @action(detail=False, methods=["get"])
    def late_submissions(self, request):

        student = get_object_or_404(
            Student,
            user=request.user
        )

        late = []

        for submission in Submission.objects.filter(student=student):

            if (
                submission.assignment.due_date and
                submission.submitted_at.date() >
                submission.assignment.due_date
            ):

                late.append(submission)

        serializer = SubmissionSerializer(
            late,
            many=True
        )

        return Response(serializer.data)