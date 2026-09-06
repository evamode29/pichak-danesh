from django.contrib import admin

from .models import ActivationCode, Content, Product, Purchase, Subscription, SubscriptionPlan


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "product_type", "price_display", "is_free", "is_active", "created_at")
    list_filter = ("product_type", "is_free", "is_active")
    search_fields = ("title", "slug", "description")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 30

    @admin.display(description="قیمت")
    def price_display(self, obj):
        return f"{obj.price:,} تومان"


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "duration_days", "price_display", "product", "is_active")
    list_filter = ("is_active", "duration_days")
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at",)
    list_per_page = 30

    @admin.display(description="قیمت")
    def price_display(self, obj):
        return f"{obj.price:,} تومان"


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "amount_display", "status", "created_at", "paid_at")
    list_filter = ("status", "product", "created_at")
    search_fields = ("user__username", "user__first_name", "user__last_name", "reference", "authority")
    readonly_fields = ("created_at", "paid_at", "reference", "authority")
    autocomplete_fields = ("user", "product")
    list_per_page = 50
    date_hierarchy = "created_at"

    @admin.display(description="مبلغ")
    def amount_display(self, obj):
        return f"{obj.amount:,} تومان"


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "starts_at", "ends_at", "source", "active_display", "is_active")
    list_filter = ("source", "is_active", "plan", "starts_at", "ends_at")
    search_fields = ("user__username", "user__first_name", "user__last_name", "plan__name")
    readonly_fields = ("created_at", "active_display")
    autocomplete_fields = ("user", "plan", "purchase")
    list_per_page = 50
    date_hierarchy = "ends_at"

    @admin.display(description="وضعیت فعلی", boolean=True)
    def active_display(self, obj):
        return obj.active_now


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ("title", "product", "is_free", "is_published", "created_at", "updated_at")
    list_filter = ("is_free", "is_published", "product")
    search_fields = ("title", "slug", "description", "body")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("product",)
    list_per_page = 30


@admin.register(ActivationCode)
class ActivationCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "plan", "days", "used_count", "max_uses", "active_display", "expires_at", "created_at")
    list_filter = ("plan", "is_active", "expires_at")
    search_fields = ("code", "plan__name")
    readonly_fields = ("used_count", "created_at", "active_display")
    autocomplete_fields = ("plan",)
    list_per_page = 50

    @admin.display(description="قابل استفاده", boolean=True)
    def active_display(self, obj):
        return obj.usable
