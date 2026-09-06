from django.contrib import admin
from django.urls import include, path

from core.api import auth_login, auth_logout, auth_me, classrooms_api, students_api, teachers_api
from core.views import (
    dashboard,
    home,
    login_view,
    logout_view,
    teacher_class_detail,
    teacher_dashboard,
    teacher_student_detail,
    teacher_students,
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", dashboard, name="dashboard"),
    path("teacher/", teacher_dashboard, name="teacher-dashboard"),
    path("teacher/students/", teacher_students, name="teacher-students"),
    path("teacher/students/<int:student_id>/", teacher_student_detail, name="teacher-student-detail"),
    path("teacher/classes/<int:classroom_id>/", teacher_class_detail, name="teacher-class-detail"),
    path("placement/", include("exams.urls")),
    path("practice/", include("practice.urls")),
    path("subscriptions/", include("subscriptions.urls")),
    path("api/v1/auth/login/", auth_login, name="api-auth-login"),
    path("api/v1/auth/me/", auth_me, name="api-auth-me"),
    path("api/v1/auth/logout/", auth_logout, name="api-auth-logout"),
    path("api/v1/classes/", classrooms_api, name="api-classrooms"),
    path("api/v1/students/", students_api, name="api-students"),
    path("api/v1/teachers/", teachers_api, name="api-teachers"),
]
