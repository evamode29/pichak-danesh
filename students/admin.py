from django.contrib import admin

from .models import ParentProfile, StudentProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "mobile",
        "grade",
        "classroom",
        "points",
        "level",
        "streak",
        "is_free",
    )
    list_filter = ("grade", "is_free", "classroom")
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "mobile",
    )


@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "mobile")
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "mobile",
    )
    filter_horizontal = ("students",)
