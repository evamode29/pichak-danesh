from django.contrib import admin

from .models import ClassRoom, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "mobile", "display_name", "is_active_profile")
    list_filter = ("role", "is_active_profile")
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "mobile",
        "display_name",
    )


@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ("name", "grade", "teacher", "academic_year", "is_active")
    list_filter = ("grade", "is_active")
    search_fields = (
        "name",
        "academic_year",
        "teacher__username",
        "teacher__first_name",
        "teacher__last_name",
    )
