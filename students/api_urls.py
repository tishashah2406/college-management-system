from rest_framework.routers import DefaultRouter
from .api_views import StudentViewSet

router = DefaultRouter()
router.register('students', StudentViewSet)

urlpatterns = router.urls