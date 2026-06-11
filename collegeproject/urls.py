from django.contrib import admin
from django.urls import path, include

from . import views

from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home),
     path(
        'about/',
        views.about,
        name='about'
    ),

    path('accounts/', include('django.contrib.auth.urls')),
    path('students/', include('students.urls')),
     path('teachers/', include('teachers.urls')),
    path('accounts/', include('accounts.urls')),   
    path('courses/', include('courses.urls')),
    path('', include('core.urls')),
    path('notifications/',include('notifications.urls')),
    
   
     path('api/', include('teachers.api_urls')),
     path('api/', include('students.api_urls')),
     path('api/courses/', include('courses.api_urls')),
    path('api/token/', TokenObtainPairView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view()),
]

#  IMPORTANT FIX
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
