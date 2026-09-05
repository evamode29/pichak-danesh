from django.contrib import admin

from .models import PlacementAttempt, PlacementQuestion, PlacementTest


@admin.register(PlacementTest)
class PlacementTestAdmin(admin.ModelAdmin):
    list_display = ("title", "grade", "duration_minutes", "is_active", "created_at")
    list_filter = ("grade", "is_active")
    search_fields = ("title",)


@admin.register(PlacementQuestion)
class PlacementQuestionAdmin(admin.ModelAdmin):
    list_display = ("test", "order", "subject", "difficulty", "correct_option", "is_active")
    list_filter = ("subject", "difficulty", "is_active")
    search_fields = ("text",)
    ordering = ("test", "order")


@admin.register(PlacementAttempt)
class PlacementAttemptAdmin(admin.ModelAdmin):
    list_display = ("student", "test", "score", "correct_answers", "total_questions", "level", "completed_at")
    list_filter = ("level", "test")
    search_fields = ("student__user__username", "student__mobile")
    readonly_fields = ("completed_at",)
