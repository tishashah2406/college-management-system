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

    # ================ LOGGED-IN DASHBOARD =================
    @method_decorator(cache_page(60 * 5))
    @method_decorator(vary_on_headers("Authorization"))
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def dashboard(self, request):

        student = Student.objects.filter(user=request.user).first()
        if not student:
            return Response({"error": "Student profile not found"}, status=404)

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

    # ================= DASHBOARD BY ID =================
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated], url_path="dashboard-by-id")
    def dashboard_by_id(self, request, pk=None):

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
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def submit_assignment(self, request):

        assignment_id = request.data.get("assignment_id")

        student = Student.objects.filter(user=request.user).first()
        if not student:
            return Response({"error": "Student not found"}, status=404)

        assignment = get_object_or_404(Assignment, id=assignment_id)

        file = request.FILES.get('file')
        if not file:
            return Response({"error": "File is required"}, status=400)

        # check enrollment
        if assignment.course not in student.courses.all():
            return Response({"error": "Not enrolled"}, status=403)

        # get existing submission safely
        submission = Submission.objects.filter(
            student=student,
            assignment=assignment
        ).first()

        if submission:
            submission.file = file
            submission.submitted_at = now()
            submission.save()
            created = False
        else:
            submission = Submission.objects.create(
                student=student,
                assignment=assignment,
                file=file,
                submitted_at=now()
            )
            created = True

        # late submission check
        
        is_late = False
        if assignment.due_date:
            is_late = submission.submitted_at.date() > assignment.due_date

        cache.clear()

        return Response({
            "message": "Submitted successfully",
            "created": created,
            "is_late": is_late,
            "submission": SubmissionSerializer(submission).data
        })
    
    #assignment_progress
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def progress_report(self,request):
        student = Student.objects.filter(user=request.user).first()


        if not student:
            return Response({"error":"student not student"},status=404)
        
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

        student = Student.objects.filter(
            user=request.user
        ).first()

        if not student:
            return Response(
                {"error": "Student not found"},
                status=404
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
    