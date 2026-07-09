from django.utils import timezone
from django.db.models import Q

from rest_framework.viewsets import ModelViewSet

from teachers.models import Teacher
from students.models import Student

from .models import Notice
from .serializers import NoticeSerializer


class NoticeViewSet(ModelViewSet):

    serializer_class = NoticeSerializer

    def get_queryset(self):

        user = self.request.user

        if user.is_superuser:

            return Notice.objects.filter(
                expiry_date__gte=timezone.now().date()
            ).order_by("-created_at")

        elif Teacher.objects.filter(user=user).exists():

            teacher = Teacher.objects.get(user=user)

            return Notice.objects.filter(

                Q(is_admin_notice=True)

                |

                Q(
                    teacher=teacher,
                    is_admin_notice=False
                ),

                expiry_date__gte=timezone.now().date()

            ).order_by("-created_at")

        elif Student.objects.filter(user=user).exists():

            student = Student.objects.get(user=user)

            return Notice.objects.filter(

                Q(is_admin_notice=True)

                |

                Q(
                    course__in=student.courses.all(),
                    is_admin_notice=False
                ),

                expiry_date__gte=timezone.now().date()

            ).distinct().order_by("-created_at")

        return Notice.objects.none()