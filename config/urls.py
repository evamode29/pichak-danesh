from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path

from core.seo import PublicSitemap, robots_txt
from core.simple_auth import login_view, logout_view
from core.simple_views import simple_home, simple_student, simple_iq_test, simple_teacher

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
]
