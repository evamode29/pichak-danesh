from django.contrib import admin

from .models import DailyMissionCompletion, PracticeAttempt, PracticeQuestion


@admin.action(description="فعال کردن سؤال‌های انتخاب‌شده")
def activate_questions(modeladmin, request, queryset):
    queryset.update(is_active=True)


@admin.action(description="غیرفعال کردن سؤال‌های انتخاب‌شده")
def deactivate_questions(modeladmin, request, queryset):
    queryset.update(is_active=False)


@admin.register(PracticeQuestion)
class PracticeQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "short_text",
        "subject",
        "level",
        "difficulty",
        "points",
        "correct_option",
        "is_active",
    )
    list_display_links = ("id", "short_text")
    list_filter = (
        "subject",
        "level",
        "difficulty",
        "is_active",
    )
    search_fields = (
        "text",
        "option_a",
        "option_b",
        "option_c",
        "option_d",
    )
    ordering = ("level", "subject", "id")
    list_per_page = 30
    list_editable = ("is_active",)
    actions = (activate_questions, deactivate_questions)
    date_hierarchy = "created_at"
    save_on_top = True
    empty_value_display = "—"

    fieldsets = (
        (
            "محتوای سؤال",
            {
                "fields": (
                    "subject",
                    "text",
                    ("option_a", "option_b"),
                    ("option_c", "option_d"),
                    "correct_option",
                )
            },
        ),
        (
            "تنظیمات آموزشی",
            {
                "fields": (
                    ("level", "difficulty"),
                    ("points", "is_active"),
                )
            },
        ),
        (
            "اطلاعات سیستم",
            {
                "classes": ("collapse",),
                "fields": ("created_at",),
            },
        ),
    )
    readonly_fields = ("created_at",)

    @admin.display(description="متن سؤال", ordering="text")
    def short_text(self, obj):
        text = " ".join(obj.text.split())
        return text[:70] + "…" if len(text) > 70 else text


@admin.register(PracticeAttempt)
class PracticeAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "question",
        "selected_option",
        "is_correct",
        "points_earned",
        "created_at",
    )
    list_filter = ("is_correct", "question__subject", "question__level", "created_at")
    search_fields = (
        "student__user__username",
        "student__user__first_name",
        "student__user__last_name",
        "student__mobile",
        "question__text",
    )
    readonly_fields = (
        "student",
        "question",
        "selected_option",
        "is_correct",
        "points_earned",
        "created_at",
    )
    ordering = ("-created_at", "-id")
    list_per_page = 50
    date_hierarchy = "created_at"


@admin.register(DailyMissionCompletion)
class DailyMissionCompletionAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "mission_code",
        "mission_date",
        "reward_xp",
        "created_at",
    )
    list_filter = ("mission_code", "mission_date")
    search_fields = (
        "student__user__username",
        "student__user__first_name",
        "student__user__last_name",
        "student__mobile",
    )
    readonly_fields = (
        "student",
        "mission_code",
        "mission_date",
        "reward_xp",
        "created_at",
    )
    ordering = ("-mission_date", "-created_at")
    list_per_page = 50
    date_hierarchy = "mission_date"
