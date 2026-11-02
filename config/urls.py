from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.views.static import serve

from core.seo import PublicSitemap, robots_txt
from core.simple_auth import login_view, logout_view
from core.simple_views import simple_home, simple_student, simple_teacher, teacher_student_detail, teacher_activities

sitemaps = {"public": PublicSitemap()}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("robots.txt", robots_txt, name="robots-txt"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("", simple_home, name="home"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("student/", simple_student, name="simple-student"),
    path("teacher/", simple_teacher, name="simple-teacher"),
    path("teacher/students/<int:student_id>/", teacher_student_detail, name="teacher-student-detail"),
    path("teacher/activities/", teacher_activities, name="teacher-activities"),
    path("media/<path:path>", serve, {"document_root": settings.MEDIA_ROOT}),
]
