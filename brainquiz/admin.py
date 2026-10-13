from django.contrib import admin
from .models import BrainQuizAttempt


@admin.register(BrainQuizAttempt)
class BrainQuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("student", "score", "correct_answers", "total_questions", "duration_seconds", "completed_at")
    list_filter = ("completed_at", "score")
    search_fields = ("student__user__first_name", "student__user__last_name", "student__user__username")
    readonly_fields = ("student", "score", "correct_answers", "total_questions", "duration_seconds", "answers", "completed_at")
