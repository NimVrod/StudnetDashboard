"""
URL configuration for StudentDashboard project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('profile/', views.profile, name='profile'),
    path('login/', views.api_login, name='login'),
    path('register/', views.register, name='register'),
    path('api/logout/', views.api_logout, name='logout'),
    path('profile/api/logout', views.api_logout, name='logout'),
    path('course/<int:course_id>/', views.course, name='course'),
    path('course/create_course/', views.create_course, name='create_course'),
    path('course/<int:course_id>/users/', views.course_users, name='course_users'),
    path('course/<int:course_id>/edituser/<int:student_id>', views.edit_user, name='edit_user'),
    path('join/<str:code>/', views.join_course, name='join_course'),
    path('course/<int:course_id>/leave/', views.leave_course, name='leave_course'),
    path('media/attachments/<int:attachment_id>', views.attachment, name='attachment'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

