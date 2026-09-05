from django.urls import path

from .views import placement_question, placement_result, placement_start

urlpatterns = [
    path("start/", placement_start, name="placement-start"),
    path("question/", placement_question, name="placement-question"),
    path("result/", placement_result, name="placement-result"),
]
