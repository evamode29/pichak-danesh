from django.urls import path
from . import views

app_name = "brainquiz"
urlpatterns = [path("", views.start, name="start"), path("play/", views.play, name="play"), path("result/<int:attempt_id>/", views.result, name="result")]
