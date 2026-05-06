from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_object_or_404

from .models import Teacher, TeacherLeave
from .serializers import TeacherSerializer

from courses.models import Assignment
from students.models import Submission
from courses.serializers import CourseSerializer, AssignmentSerializer, SubmissionSerializer


class TeacherViewSet(ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

    # ================= LOGGED-IN DASHBOARD =================
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def dashboard(self, request):

        teacher = get_object_or_404(Teacher, user=request.user)

        courses = teacher.courses.all()

        assignments_qs = Assignment.objects.filter(course__in=courses)

        submissions_qs = Submission.objects.filter(
    assignment__course__in=courses
)

        leaves = TeacherLeave.objects.filter(teacher=teacher)

        return Response({
            "teacher": TeacherSerializer(teacher).data,
            "courses": CourseSerializer(courses, many=True).data,
            "assignments": AssignmentSerializer(assignments_qs, many=True).data,
            "submissions": SubmissionSerializer(submissions_qs, many=True).data,
            "leaves": list(leaves.values()),
        })

    # ================= DASHBOARD BY ID =================
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def dashboard_by_id(self, request, pk=None):

        teacher = get_object_or_404(Teacher, id=pk)

        courses = teacher.courses.all()

        assignments_qs = Assignment.objects.filter(course__in=courses)

        submissions_qs = Submission.objects.filter(
    assignment__course__in=courses
)

        leaves = TeacherLeave.objects.filter(teacher=teacher)

        return Response({
            "teacher": TeacherSerializer(teacher).data,
            "courses": CourseSerializer(courses, many=True).data,
            "assignments": AssignmentSerializer(assignments_qs, many=True).data,
            "submissions": SubmissionSerializer(submissions_qs, many=True).data,
            "leaves": list(leaves.values()),
            
        })
   