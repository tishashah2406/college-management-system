from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.utils import timezone
from django.db.models import Q

from .models import Notice
from .serializers import NoticeSerializer

from teachers.models import Teacher
from students.models import Student



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