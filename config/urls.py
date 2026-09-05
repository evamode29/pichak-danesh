from django.contrib import admin
from django.urls import path

from core.api import auth_login, auth_logout, auth_me, classrooms_api, students_api, teachers_api
from core.views import home


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("api/v1/auth/login/", auth_login, name="api-auth-login"),
    path("api/v1/auth/me/", auth_me, name="api-auth-me"),
    path("api/v1/auth/logout/", auth_logout, name="api-auth-logout"),
    path("api/v1/classes/", classrooms_api, name="api-classrooms"),
    path("api/v1/students/", students_api, name="api-students"),
    path("api/v1/teachers/", teachers_api, name="api-teachers"),
]
