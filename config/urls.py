from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path

from core.seo import PublicSitemap, robots_txt
from core.simple_auth import login_view, logout_view
from core.simple_views import simple_home, simple_student, simple_iq_test, simple_teacher, teacher_test_manager, student_test_list, student_take_test

sitemaps = {"public": PublicSitemap()}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("robots.txt", robots_txt, name="robots-txt"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("", simple_home, name="home"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("student/", simple_student, name="simple-student"),
    path("iq/", simple_iq_test, name="simple-iq"),
    path("teacher/", simple_teacher, name="simple-teacher"),
    path("teacher/tests/", teacher_test_manager, name="teacher-test-manager"),
    path("tests/", student_test_list, name="student-test-list"),
    path("tests/<int:test_id>/", student_take_test, name="student-take-test"),
]
