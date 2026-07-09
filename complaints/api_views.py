from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from students.models import Student
from teachers.models import Teacher
from notifications.models import Notification

from .models import Complaint
from .serializers import ComplaintSerializer


class ComplaintViewSet(ModelViewSet):

    serializer_class = ComplaintSerializer
    queryset = Complaint.objects.all().order_by("-created_at")

    def get_queryset(self):

        user = self.request.user

        # Admin can see all complaints
        if user.is_superuser:
            return Complaint.objects.all().order_by("-created_at")

        # Student can see only their complaints
        elif Student.objects.filter(user=user).exists():

            student = Student.objects.get(user=user)

            return Complaint.objects.filter(
                student=student
            ).order_by("-created_at")

        # Teacher can see only assigned complaints
        elif Teacher.objects.filter(user=user).exists():

            teacher = Teacher.objects.get(user=user)

            return Complaint.objects.filter(
                assigned_teacher=teacher
            ).order_by("-created_at")

        return Complaint.objects.none()
    # -------------------------
    # CREATE COMPLAINT
    # -------------------------

    def create(self, request, *args, **kwargs):

        student = get_object_or_404(
            Student,
            user=request.user
        )

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        complaint = serializer.save(
            student=student
        )

        # Assign Complaint

        if complaint.category in [

            "Fees",
            "Technical",
            "Hostel",
            "Other"

        ]:

            admin = User.objects.filter(
                is_superuser=True
            ).first()

            complaint.assigned_admin = admin

        else:

            teacher = Teacher.objects.filter(
                courses=complaint.course
            ).first()

            complaint.assigned_teacher = teacher

        complaint.save()

        # Notifications

        if complaint.assigned_admin:

            Notification.objects.create(

                user=complaint.assigned_admin,

                title="New Complaint",

                message=f"New complaint '{complaint.title}' submitted."

            )

        if complaint.assigned_teacher:

            Notification.objects.create(

                user=complaint.assigned_teacher.user,

                title="New Complaint",

                message=f"Complaint '{complaint.title}' assigned to you."

            )

        return Response(

            {

                "message": "Complaint created successfully.",

                "data": self.get_serializer(
                    complaint
                ).data

            },

            status=status.HTTP_201_CREATED

        )

    # -------------------------
    # RETRIEVE
    # -------------------------

    def retrieve(self, request, *args, **kwargs):

        complaint = self.get_object()

        serializer = self.get_serializer(
            complaint
        )

        return Response(
            serializer.data
        )

    # -------------------------
    # UPDATE (PATCH)
    # -------------------------

    def partial_update(self, request, *args, **kwargs):

        complaint = self.get_object()

        serializer = self.get_serializer(

            complaint,

            data=request.data,

            partial=True

        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            serializer.data
        )
    
        # -------------------------
    # DELETE COMPLAINT
    # -------------------------

    def destroy(self, request, *args, **kwargs):

        complaint = self.get_object()

        complaint.delete()

        return Response(
            {
                "message": "Complaint deleted successfully."
            },
            status=status.HTTP_204_NO_CONTENT
        )

    # -------------------------
    # RESOLVE COMPLAINT
    # -------------------------

    @action(detail=True, methods=["put"])
    def resolve(self, request, pk=None):

        complaint = self.get_object()

        # Permission Check

        if request.user.is_superuser:
            pass

        elif (
            complaint.assigned_teacher
            and complaint.assigned_teacher.user == request.user
        ):
            pass

        else:

            return Response(
                {
                    "error": "You do not have permission to update this complaint."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        old_status = complaint.status

        complaint.status = request.data.get(
            "status",
            complaint.status
        )

        complaint.reply = request.data.get(
            "reply",
            complaint.reply
        )

        complaint.admin_remarks = request.data.get(
            "admin_remarks",
            complaint.admin_remarks
        )

        if complaint.status == "Resolved":

            complaint.resolved_at = timezone.now()

        complaint.save()

        # Status Notification

        if old_status != complaint.status:

            Notification.objects.create(
                user=complaint.student.user,
                title="Complaint Updated",
                message=f"Your complaint '{complaint.title}' is now {complaint.status}."
            )

        # Reply Notification

        if complaint.reply:

            Notification.objects.create(
                user=complaint.student.user,
                title="Complaint Reply",
                message=f"A reply has been added to your complaint '{complaint.title}'."
            )

        serializer = self.get_serializer(
            complaint
        )

        return Response(
            {
                "message": "Complaint updated successfully.",
                "data": serializer.data
            }
        )

    # -------------------------
    # MY COMPLAINTS
    # -------------------------

    @action(detail=False, methods=["get"])
    def my(self, request):

        student = get_object_or_404(
            Student,
            user=request.user
        )

        complaints = Complaint.objects.filter(
            student=student
        ).order_by("-created_at")

        serializer = self.get_serializer(
            complaints,
            many=True
        )

        return Response(
            {
                "total": complaints.count(),

                "pending": complaints.filter(
                    status="Pending"
                ).count(),

                "progress": complaints.filter(
                    status="In Progress"
                ).count(),

                "resolved": complaints.filter(
                    status="Resolved"
                ).count(),

                "complaints": serializer.data
            }
        )

    # -------------------------
    # TEACHER COMPLAINTS
    # -------------------------

    @action(detail=False, methods=["get"])
    def teacher(self, request):

        teacher = get_object_or_404(
            Teacher,
            user=request.user
        )

        complaints = Complaint.objects.filter(
            assigned_teacher=teacher
        ).order_by("-created_at")

        serializer = self.get_serializer(
            complaints,
            many=True
        )

        return Response(
            serializer.data
        )

    # -------------------------
    # ADMIN COMPLAINTS
    # -------------------------

    @action(detail=False, methods=["get"])
    def admin(self, request):

        complaints = Complaint.objects.filter(
            assigned_admin=request.user
        ).order_by("-created_at")

        serializer = self.get_serializer(
            complaints,
            many=True
        )

        return Response(
            serializer.data
        )
    
        # -------------------------
    # COMPLAINT STATISTICS
    # -------------------------

    @action(detail=False, methods=["get"])
    def statistics(self, request):

        complaints = self.get_queryset()
        return Response({

            "total": complaints.count(),

            "pending": complaints.filter(
                status="Pending"
            ).count(),

            "in_progress": complaints.filter(
                status="In Progress"
            ).count(),

            "resolved": complaints.filter(
                status="Resolved"
            ).count()

        })

    # -------------------------
    # COMPLAINT COUNT
    # -------------------------

    @action(detail=False, methods=["get"])
    def count(self, request):

        return Response({

            "count": self.get_queryset().count()

        })

    # -------------------------
    # SEARCH COMPLAINT
    # -------------------------

    @action(detail=False, methods=["get"])
    def search(self, request):

        query = request.query_params.get(
            "q",
            ""
        )

        status_filter = request.query_params.get(
            "status"
        )

        category = request.query_params.get(
            "category"
        )

        complaints = self.get_queryset().count()

        if query:

            complaints = complaints.filter(

                Q(title__icontains=query)

                |

                Q(description__icontains=query)

            )

        if status_filter:

            complaints = complaints.filter(
                status=status_filter
            )

        if category:

            complaints = complaints.filter(
                category=category
            )

        serializer = self.get_serializer(

            complaints,

            many=True

        )

        return Response(
            serializer.data
        )