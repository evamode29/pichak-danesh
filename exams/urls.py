from django.urls import path

from .views import (
    placement_answer_key,
    placement_question,
    placement_result,
    placement_result_history,
    placement_start,
    placement_history,
    teacher_approve_placement,
    teacher_approve_placement_repeat,
    teacher_class_diagnostic,
)

urlpatterns = [
    path("start/", placement_start, name="placement-start"),
    path("question/", placement_question, name="placement-question"),
    path("result/", placement_result, name="placement-result"),
    path("history/", placement_history, name="placement-history"),
    path("history/<int:attempt_id>/", placement_result_history, name="placement-result-history"),
    path("answer-key/<int:attempt_id>/", placement_answer_key, name="placement-answer-key"),
    path("teacher/approve/<int:attempt_id>/", teacher_approve_placement, name="teacher-approve-placement"),
    path("teacher/approve-repeat/<int:attempt_id>/", teacher_approve_placement_repeat, name="teacher-approve-placement-repeat"),
    path("teacher/classes/<int:classroom_id>/diagnostic/", teacher_class_diagnostic, name="teacher-class-diagnostic"),
]
