from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.views.static import serve

from core.seo import PublicSitemap, robots_txt
from core.simple_auth import login_view, logout_view
from core.simple_views import simple_home, simple_iq_test, simple_student, simple_teacher, teacher_student_detail, teacher_activities, teacher_test_manager, student_test_list, student_take_test, download_student_submission, download_task_instruction, block_public_homework_media

sitemaps = {"public": PublicSitemap()}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("robots.txt", robots_txt, name="robots-txt"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("", simple_home, name="home"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("student/", simple_student, name="simple-student"),
    path("student/iq/", simple_iq_test, name="simple-iq"),
    path("teacher/", simple_teacher, name="simple-teacher"),
    path("teacher/students/<int:student_id>/", teacher_student_detail, name="teacher-student-detail"),
    path("teacher/activities/", teacher_activities, name="teacher-activities"),
    path("teacher/tests/", teacher_test_manager, name="teacher-test-manager"),
    path("student/tests/", student_test_list, name="student-test-list"),
    path("student/tests/<int:test_id>/", student_take_test, name="student-take-test"),
    path("homework/submissions/<int:record_id>/file/", download_student_submission, name="homework-submission-file"),
    path("homework/instructions/<int:task_id>/file/", download_task_instruction, name="homework-instruction-file"),
    path("media/homework/<path:path>", block_public_homework_media, name="block-public-homework-media"),
    path("media/<path:path>", serve, {"document_root": settings.MEDIA_ROOT}),
]
