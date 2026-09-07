from django.contrib import admin
from django.utils import timezone

from .models import ParentProfile, StudentProfile
from subscriptions.models import Purchase, Subscription


class SubscriptionInline(admin.TabularInline):
    model = Subscription
    extra = 0
    fields = ("plan", "starts_at", "ends_at", "source", "is_active", "active_now_display")
    readonly_fields = ("active_now_display",)
    autocomplete_fields = ("plan",)
    ordering = ("-ends_at", "-id")
    classes = ("collapse",)

    @admin.display(description="فعال اکنون", boolean=True)
    def active_now_display(self, obj):
        return obj.active_now


class PurchaseInline(admin.TabularInline):
    model = Purchase
    extra = 0
    fields = ("product", "amount", "status", "reference", "created_at", "paid_at")
    readonly_fields = ("created_at", "paid_at", "reference")
    autocomplete_fields = ("product",)
    ordering = ("-created_at", "-id")
    classes = ("collapse",)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "student_name",
        "mobile",
        "grade",
        "classroom",
        "subscription_status",
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
    autocomplete_fields = ("user", "classroom")
    inlines = (SubscriptionInline, PurchaseInline)

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
                "description": "فعال بودن این گزینه به معنی رایگان بودن حساب دانش‌آموز است؛ اشتراک‌های خریداری‌شده در بخش اشتراک‌ها مدیریت می‌شوند.",
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

    @admin.display(description="اشتراک")
    def subscription_status(self, obj):
        subscription = Subscription.active_for(obj.user)
        if not subscription:
            return "بدون اشتراک فعال"
        remaining = max(0, (subscription.ends_at - timezone.now()).days)
        return f"{subscription.plan.name} · {remaining} روز باقی‌مانده"


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
