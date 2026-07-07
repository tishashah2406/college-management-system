from time import timezone

from django.db.models import Avg
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_object_or_404

from .models import Teacher, TeacherLeave
from .serializers import TeacherSerializer

from courses.models import Assignment
from students.models import Submission, Student

from courses.serializers import (
    CourseSerializer,
    AssignmentSerializer,
    SubmissionSerializer
)


class TeacherViewSet(ModelViewSet):

    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

    # ================= TEACHER DASHBOARD =================
    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )

    def dashboard(self, request):

        teacher = get_object_or_404(
            Teacher,
            user=request.user
        )

        courses = teacher.courses.all()

        assignments_qs = Assignment.objects.filter(
            course__in=courses
        )

        submissions_qs = Submission.objects.filter(
            assignment__course__in=courses
        )

        leaves = TeacherLeave.objects.filter(
            teacher=teacher
        )

        # ================= COUNTS =================

        total_courses = courses.count()

        total_assignments = assignments_qs.count()

        total_submissions = submissions_qs.count()

        # ================= STUDENTS =================

        total_students = Student.objects.filter(
            courses__in=courses
        ).distinct().count()

        # ================= PENDING SUBMISSIONS =================

        checked_submissions = submissions_qs.exclude(
            grade__isnull=True
        ).count()

        pending_submissions = submissions_qs.filter(
            grade__isnull=True
        ).count()

        # ================= AVERAGE GRADE =================

        average_grade = submissions_qs.aggregate(
            Avg("grade")
        )["grade__avg"] or 0

        # ================= COURSE ANALYTICS =================

        course_analytics = []

        for course in courses:

            assignments_count = Assignment.objects.filter(
                course=course
            ).count()

            submissions_count = Submission.objects.filter(
                assignment__course=course
            ).count()

            students_count = Student.objects.filter(
                courses=course
            ).distinct().count()

            progress = 0

            total_possible_submissions = (
                students_count * assignments_count
            )

            if total_possible_submissions > 0:

                progress = (
                    submissions_count /
                    total_possible_submissions
                ) * 100

            course_analytics.append({

                "course_id":
                    course.id,

                "course_name":
                    course.name,

                "students":
                    students_count,

                "assignments":
                    assignments_count,

                "submissions":
                    submissions_count,

                "completion_percentage":
                    round(progress, 2)
            })
 
        # ================= TOP STUDENTS =================

        top_students = []

        students = Student.objects.filter(
            courses__in=courses
        ).distinct()

        for student in students:

            student_submissions = Submission.objects.filter(
                student=student,
                assignment__course__in=courses
            )

            avg_grade = student_submissions.aggregate(
                Avg("grade")
            )["grade__avg"] or 0

            completed = student_submissions.count()

            top_students.append({

                "student_id":
                    student.id,

                "student_name":
                    student.user.username,

                "completed_assignments":
                    completed,

                "average_grade":
                    round(avg_grade, 2)
            })

        top_students = sorted(
            top_students,
            key=lambda x: x["average_grade"],
            reverse=True
        )

        # ================= RECENT SUBMISSIONS =================

        recent_submissions = submissions_qs.order_by(
            "-submitted_at"
        )[:5]

        # ================= CHART DATA =================

        chart_data = {

            "dashboard_cards": {

                "total_courses":
                    total_courses,
                    
                "total_students":
                    total_students,

                "total_assignments":
                    total_assignments,

                "total_submissions":
                    total_submissions,

                "pending_submissions":
                    pending_submissions,

                "checked_submissions":
                    checked_submissions,

                "average_grade":
                    round(average_grade, 2)
            },

            "submission_chart": {

            "total_submitted":
                total_submissions,

            "checked":
                checked_submissions,

            "pending_checking":
                pending_submissions
        }
        }

        # ================= FINAL RESPONSE =================

        return Response({

            "teacher":
                TeacherSerializer(teacher).data,

            "courses":
                CourseSerializer(courses, many=True).data,

            "assignments":
                AssignmentSerializer(
                    assignments_qs,
                    many=True
                ).data,

            "recent_submissions":
                SubmissionSerializer(
                    recent_submissions,
                    many=True
                ).data,

            "leaves":
                list(leaves.values()),

            "analytics": {

                "total_courses":
                    total_courses,

                "total_students":
                    total_students,

                "total_assignments":
                    total_assignments,

                "total_submissions":
                    total_submissions,

                "pending_submissions":
                    pending_submissions,

                "checked_submissions":
                    checked_submissions,

                "average_grade":
                    round(average_grade, 2)
            },

            "course_analytics":
                course_analytics,

            "top_students":
                top_students[:5],

            "charts":
                chart_data
        })
    
    @action(detail=False, methods=["get"])
    def profile(self, request):

        teacher = get_object_or_404(
            Teacher,
            user=request.user
        )

        serializer = TeacherSerializer(teacher)

        return Response(serializer.data)
    
    @action(detail=False, methods=["patch"])
    def update_profile(self, request):

        teacher = get_object_or_404(
            Teacher,
            user=request.user
        )

        serializer = TeacherSerializer(
            teacher,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
    
    @action(detail=False, methods=["get"])
    def students(self, request):

        teacher = get_object_or_404(
            Teacher,
            user=request.user
        )

        students = Student.objects.filter(
            courses__in=teacher.courses.all()
        ).distinct()

        from students.serializers import StudentSerializer

        serializer = StudentSerializer(
            students,
            many=True
        )

        return Response(serializer.data)
    
    @action(detail=False, methods=["get"])
    def pending_submissions(self, request):

        teacher = Teacher.objects.get(
            user=request.user
        )

        submissions = Submission.objects.filter(
            assignment__course__in=teacher.courses.all(),
            grade__isnull=True
        )

        serializer = SubmissionSerializer(
            submissions,
            many=True
        )

        return Response(serializer.data)
    
    @action(detail=False, methods=["get"])
    def checked_submissions(self, request):

        teacher = Teacher.objects.get(
            user=request.user
        )

        submissions = Submission.objects.filter(
            assignment__course__in=teacher.courses.all()
        ).exclude(
            grade__isnull=True
        )

        serializer = SubmissionSerializer(
            submissions,
            many=True
        )

        return Response(serializer.data)
    
    @action(detail=True, methods=["patch"])
    def grade_submission(self, request, pk=None):

        submission = get_object_or_404(
            Submission,
            pk=pk
        )

        submission.grade = request.data.get("grade")
        submission.feedback = request.data.get("feedback")

        submission.save()

        return Response({
            "message": "Assignment graded successfully."
        })
    
    @action(detail=False, methods=["get"])
    def upcoming_assignments(self, request):

        teacher = Teacher.objects.get(
            user=request.user
        )

        assignments = Assignment.objects.filter(
            course__in=teacher.courses.all(),
            due_date__gte=timezone.now().date()
        ).order_by("due_date")

        serializer = AssignmentSerializer(
            assignments,
            many=True
        )

        return Response(serializer.data)
    
    @action(detail=False,methods=["get"])
    def upcoming_assignments(self,request):

        teacher = Teacher.objects.get(
            user=request.user
        )

        assignments = Assignment.objects.filter(
            course__in=teacher.courses.all(),
            due_date__gte=timezone.now().date()
        ).order_by("due_date")

        serializer = AssignmentSerializer(
            assignments,
            many=True
        )

        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def leave_history(self, request):

        teacher = Teacher.objects.get(
            user=request.user
        )

        leaves = TeacherLeave.objects.filter(
            teacher=teacher
        )

        return Response(list(leaves.values()))
    
    @action(detail=False, methods=["get"])
    def student_count(self, request):

        teacher = Teacher.objects.get(
            user=request.user
        )

        data = []

        for course in teacher.courses.all():

            data.append({

                "course": course.name,

                "students": Student.objects.filter(
                    courses=course
                ).count()

            })

        return Response(data)
    
    @action(detail=False, methods=["get"])
    def course_grades(self, request):

        teacher = Teacher.objects.get(
            user=request.user
        )

        data = []

        for course in teacher.courses.all():

            avg = Submission.objects.filter(
                assignment__course=course
            ).aggregate(
                Avg("grade")
            )["grade__avg"] or 0

            data.append({

                "course": course.name,

                "average_grade": round(avg,2)

            })

        return Response(data)
    
    @action(detail=False, methods=["get"])
    def search_student(self, request):

        keyword = request.query_params.get("q","")

        teacher = Teacher.objects.get(
            user=request.user
        )

        students = Student.objects.filter(
            courses__in=teacher.courses.all(),
            user__username__icontains=keyword
        ).distinct()

        from students.serializers import StudentSerializer

        serializer = StudentSerializer(
            students,
            many=True
        )

        return Response(serializer.data)
    
    @action(detail=False, methods=["get"])
    def statistics(self, request):

        teacher = Teacher.objects.get(
            user=request.user
        )

        return Response({

            "courses": teacher.courses.count(),

            "students": Student.objects.filter(
                courses__in=teacher.courses.all()
            ).distinct().count(),

            "assignments": Assignment.objects.filter(
                course__in=teacher.courses.all()
            ).count(),

            "submissions": Submission.objects.filter(
                assignment__course__in=teacher.courses.all()
            ).count()

        })
            
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class MyCoursesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        teacher = Teacher.objects.get(user=request.user)

        courses = teacher.courses.all()

        serializer = CourseSerializer(
            courses,
            many=True
        )

        return Response(serializer.data)
    