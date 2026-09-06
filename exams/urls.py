from django.urls import path

from .views import (
    placement_answer_key,
    placement_question,
    placement_result,
    placement_start,
    teacher_approve_placement,
)

urlpatterns = [
    path("start/", placement_start, name="placement-start"),
    path("question/", placement_question, name="placement-question"),
    path("result/", placement_result, name="placement-result"),
    path("answer-key/<int:attempt_id>/", placement_answer_key, name="placement-answer-key"),
    path("teacher/approve/<int:attempt_id>/", teacher_approve_placement, name="teacher-approve-placement"),
]
