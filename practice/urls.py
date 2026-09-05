from django.urls import path

from .views import practice_question, practice_result, practice_start


urlpatterns = [
    path("", practice_start, name="practice-start"),
    path("question/", practice_question, name="practice-question"),
    path("result/", practice_result, name="practice-result"),
]
