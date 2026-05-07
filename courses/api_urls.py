from rest_framework.routers import DefaultRouter
from .api_views import CourseViewSet, AssignmentViewSet,  NoteViewSet

router = DefaultRouter()

router.register('courses', CourseViewSet, basename='courses')
router.register('assignments', AssignmentViewSet, basename='assignments')
router.register('notes',NoteViewSet,basename='notes')

urlpatterns = router.urls