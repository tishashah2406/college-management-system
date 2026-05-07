from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils.timezone import now

from .models import Student, CourseProgress, Submission
from courses.models import Assignment
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

    # ================= LOGGED-IN DASHBOARD =================
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

        return Response({
            "message": "Submitted successfully",
            "created": created,
            "is_late": is_late,
            "submission": SubmissionSerializer(submission).data
        })