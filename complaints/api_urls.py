from django.urls import path
from .api_views import (
    CreateComplaintAPIView,
    MyComplaintAPIView,
    TeacherComplaintAPIView,
    AdminComplaintAPIView,
    ResolveComplaintAPIView,
    UpdateComplaintAPIView,   # add this
)

urlpatterns = [
    path("create/", CreateComplaintAPIView.as_view(), name="create-complaint-api"),
    path("my/", MyComplaintAPIView.as_view(), name="my-complaints-api"),
    path("teacher/", TeacherComplaintAPIView.as_view(), name="teacher-complaints-api"),
    path("admin/", AdminComplaintAPIView.as_view(), name="admin-complaints-api"),
    path("resolve/<int:id>/", ResolveComplaintAPIView.as_view(), name="resolve-complaint-api"),

    path("update/<int:id>/", UpdateComplaintAPIView.as_view(), name="update-complaint-api"),
]