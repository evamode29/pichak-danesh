from django.contrib import admin

from .models import PracticeAttempt, PracticeQuestion


@admin.register(PracticeQuestion)
class PracticeQuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "level", "difficulty", "points", "is_active")
    list_filter = ("subject", "level", "difficulty", "is_active")
    search_fields = ("text",)
    ordering = ("level", "subject", "id")


@admin.register(PracticeAttempt)
class PracticeAttemptAdmin(admin.ModelAdmin):
    list_display = ("student", "question", "is_correct", "points_earned", "created_at")
    list_filter = ("is_correct", "created_at")
    search_fields = ("student__user__username", "student__mobile")
    readonly_fields = ("created_at",)
