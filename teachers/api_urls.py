from rest_framework.routers import DefaultRouter
from .api_views import TeacherViewSet,  MyCoursesAPIView
from django . urls import path   # adjust file name if needed

router = DefaultRouter()
router.register('teachers', TeacherViewSet)

urlpatterns = router.urls

urlpatterns = router.urls + [
    path(
        "my-courses/",
        MyCoursesAPIView.as_view(),
        name="my-courses-api"
    ),
]