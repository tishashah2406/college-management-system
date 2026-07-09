from rest_framework.routers import DefaultRouter
from .api_views import NoticeViewSet

router = DefaultRouter()

router.register(
    "notices",
    NoticeViewSet,
    basename="notices"
)

urlpatterns = router.urls