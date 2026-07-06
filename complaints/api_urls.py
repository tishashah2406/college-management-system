from django.urls import path

from .api_views import (

    CreateComplaintAPIView,
    MyComplaintAPIView,
    TeacherComplaintAPIView,
    AdminComplaintAPIView,
    ResolveComplaintAPIView,
    UpdateComplaintAPIView,

    ComplaintDetailAPIView,
    DeleteComplaintAPIView,
    ComplaintStatisticsAPIView,
    ComplaintCountAPIView,
    SearchComplaintAPIView,
)

urlpatterns = [

    path(
        "create/",
        CreateComplaintAPIView.as_view(),
        name="create-complaint-api"
    ),

    path(
        "my/",
        MyComplaintAPIView.as_view(),
        name="my-complaint-api"
    ),

    path(
        "teacher/",
        TeacherComplaintAPIView.as_view(),
        name="teacher-complaint-api"
    ),

    path(
        "admin/",
        AdminComplaintAPIView.as_view(),
        name="admin-complaint-api"
    ),

    path(
        "<int:id>/",
        ComplaintDetailAPIView.as_view(),
        name="complaint-detail-api"
    ),

    path(
        "<int:id>/update/",
        UpdateComplaintAPIView.as_view(),
        name="update-complaint-api"
    ),

    path(
        "<int:id>/resolve/",
        ResolveComplaintAPIView.as_view(),
        name="resolve-complaint-api"
    ),

    path(
        "<int:id>/delete/",
        DeleteComplaintAPIView.as_view(),
        name="delete-complaint-api"
    ),

    path(
        "statistics/",
        ComplaintStatisticsAPIView.as_view(),
        name="complaint-statistics-api"
    ),

    path(
        "count/",
        ComplaintCountAPIView.as_view(),
        name="complaint-count-api"
    ),

    path(
        "search/",
        SearchComplaintAPIView.as_view(),
        name="search-complaint-api"
    ),
]