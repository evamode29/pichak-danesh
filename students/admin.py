from django.contrib import admin

from .models import ParentProfile, StudentProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "student_name",
        "mobile",
        "grade",
        "classroom",
        "points",
        "xp",
        "level",
        "streak",
        "is_free",
    )
    list_display_links = ("student_name", "mobile")
    list_filter = ("grade", "level", "is_free", "classroom")
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "mobile",
    )
    ordering = ("-points", "-xp", "id")
    list_per_page = 30
    save_on_top = True
    empty_value_display = "—"

    fieldsets = (
        (
            "اطلاعات دانش‌آموز",
            {
                "fields": (
                    "user",
                    "mobile",
                    ("grade", "classroom"),
                )
            },
        ),
        (
            "پیشرفت آموزشی",
            {
                "fields": (
                    ("points", "xp"),
                    ("level", "streak"),
                )
            },
        ),
        (
            "دسترسی",
            {
                "fields": ("is_free",),
            },
        ),
        (
            "اطلاعات سیستم",
            {
                "classes": ("collapse",),
                "fields": ("created_at", "updated_at"),
            },
        ),
    )
    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="دانش‌آموز", ordering="user__first_name")
    def student_name(self, obj):
        return obj.user.get_full_name() or obj.user.username


@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ("parent_name", "mobile", "student_count", "created_at")
    list_display_links = ("parent_name", "mobile")
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "mobile",
    )
    list_per_page = 30
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("students",)

    @admin.display(description="والد/سرپرست", ordering="user__first_name")
    def parent_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    @admin.display(description="تعداد فرزندان")
    def student_count(self, obj):
        return obj.students.count()
