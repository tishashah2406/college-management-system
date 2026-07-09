from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api_views import TimetableViewSet

router = DefaultRouter()

router.register(
    "timetables",
    TimetableViewSet,
    basename="timetable"
)

urlpatterns = [
    path("", include(router.urls)),
]