from rest_framework.routers import DefaultRouter
from .api_views import TeacherViewSet   # adjust file name if needed

router = DefaultRouter()
router.register('teachers', TeacherViewSet)

urlpatterns = router.urls