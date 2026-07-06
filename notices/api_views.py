from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.utils import timezone
from django.db.models import Q

from .models import Notice
from .serializers import NoticeSerializer

from teachers.models import Teacher
from students.models import Student

from django.shortcuts import get_object_or_404
class NoticeListAPIView(APIView):

    def get(self, request):

        user = request.user


        # Admin sees all notices
        if user.is_superuser:

            notices = Notice.objects.filter(
                expiry_date__gte=timezone.now().date()
            )


        # Teacher notices
        elif Teacher.objects.filter(user=user).exists():

            teacher = Teacher.objects.get(
                user=user
            )

            notices = Notice.objects.filter(

                Q(is_admin_notice=True)

                |

                Q(
                    teacher=teacher,
                    is_admin_notice=False
                ),

                expiry_date__gte=timezone.now().date()

            )


        # Student notices
        elif Student.objects.filter(user=user).exists():

            student = Student.objects.get(
                user=user
            )


            notices = Notice.objects.filter(

                Q(is_admin_notice=True)

                |

                Q(
                    course__in=student.courses.all(),
                    is_admin_notice=False
                ),

                expiry_date__gte=timezone.now().date()

            ).distinct()


        else:

            return Response(
                {
                    "error":"User role not found"
                },
                status=status.HTTP_403_FORBIDDEN
            )


        serializer = NoticeSerializer(
            notices.order_by("-created_at"),
            many=True
        )


        return Response(
            serializer.data
        )

class NoticeDetailAPIView(APIView):

    def get(self, request, id):

        user = request.user

        # Admin
        if user.is_superuser:

            notice = get_object_or_404(
                Notice,
                id=id,
                expiry_date__gte=timezone.now().date()
            )

        # Teacher
        elif Teacher.objects.filter(user=user).exists():

            teacher = Teacher.objects.get(user=user)

            notice = get_object_or_404(

                Notice,

                Q(is_admin_notice=True)
                |
                Q(
                    teacher=teacher,
                    is_admin_notice=False
                ),

                id=id,
                expiry_date__gte=timezone.now().date()

            )

        # Student
        elif Student.objects.filter(user=user).exists():

            student = Student.objects.get(user=user)

            notice = get_object_or_404(

                Notice,

                Q(is_admin_notice=True)
                |
                Q(
                    course__in=student.courses.all(),
                    is_admin_notice=False
                ),

                id=id,
                expiry_date__gte=timezone.now().date()

            )

        else:

            return Response(
                {"error": "User role not found"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = NoticeSerializer(notice)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
    
class CreateNoticeAPIView(APIView):

    def post(self, request):

        serializer = NoticeSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
class UpdateNoticeAPIView(APIView):

    def put(self, request, id):

        notice = get_object_or_404(
            Notice,
            id=id
        )

        serializer = NoticeSerializer(
            notice,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, id):

        notice = get_object_or_404(
            Notice,
            id=id
        )

        serializer = NoticeSerializer(
            notice,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
class DeleteNoticeAPIView(APIView):

    def delete(self, request, id):

        notice = get_object_or_404(
            Notice,
            id=id
        )

        notice.delete()

        return Response(
            {
                "message": "Notice deleted successfully."
            },
            status=status.HTTP_204_NO_CONTENT
        )