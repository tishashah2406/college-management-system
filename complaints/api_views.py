from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone

from students.models import Student
from teachers.models import Teacher
from notifications.models import Notification

from .models import Complaint
from .serializers import ComplaintSerializer

class CreateComplaintAPIView(APIView):

    def post(self, request):

        student = get_object_or_404(
            Student,
            user=request.user
        )

        serializer = ComplaintSerializer(
            data=request.data
        )

        if serializer.is_valid():

            complaint = serializer.save(
                student=student
            )

            # Assign complaint
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
                    "data": ComplaintSerializer(complaint).data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    

class MyComplaintAPIView(APIView):

    def get(self, request):

        student = get_object_or_404(
            Student,
            user=request.user
        )

        complaints = Complaint.objects.filter(
            student=student
        ).order_by("-created_at")

        serializer = ComplaintSerializer(
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
            },
            status=status.HTTP_200_OK
        )
    
class TeacherComplaintAPIView(APIView):

    def get(self, request):

        teacher = get_object_or_404(
            Teacher,
            user=request.user
        )

        complaints = Complaint.objects.filter(
            assigned_teacher=teacher
        ).order_by("-created_at")

        serializer = ComplaintSerializer(
            complaints,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
    
class AdminComplaintAPIView(APIView):

    def get(self, request):

        complaints = Complaint.objects.filter(
            assigned_admin=request.user
        ).order_by("-created_at")

        serializer = ComplaintSerializer(
            complaints,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

class ResolveComplaintAPIView(APIView):

    def put(self, request, id):

        complaint = get_object_or_404(
            Complaint,
            id=id
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
                message=f"A reply was added to your complaint '{complaint.title}'."
            )

        serializer = ComplaintSerializer(
            complaint
        )

        return Response(
            {
                "message": "Complaint updated successfully.",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Complaint
from .serializers import ComplaintSerializer


class UpdateComplaintAPIView(APIView):

    def patch(self, request, id):

        complaint = Complaint.objects.get(id=id)

        data = {
            "title": request.data.get("title", complaint.title),
            "description": request.data.get("description", complaint.description),
            "reply": request.data.get("reply", complaint.reply),
        }

        serializer = ComplaintSerializer(
            complaint,
            data=data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )