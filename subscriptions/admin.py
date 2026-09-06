from django.contrib import admin

from .models import ActivationCode, Content, Product, Purchase, Subscription, SubscriptionPlan


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "product_type", "price", "is_free", "is_active")
    list_filter = ("product_type", "is_free", "is_active")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "duration_days", "price", "is_active")
    list_filter = ("duration_days", "is_active")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "amount", "status", "created_at", "paid_at")
    list_filter = ("status", "product")
    search_fields = ("user__username", "user__first_name", "user__last_name", "reference")
    readonly_fields = ("created_at",)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "starts_at", "ends_at", "source", "is_active", "active_now")
    list_filter = ("source", "is_active", "plan")
    search_fields = ("user__username", "user__first_name", "user__last_name")
    readonly_fields = ("created_at",)


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ("title", "product", "is_free", "is_published", "created_at")
    list_filter = ("is_free", "is_published", "product")
    search_fields = ("title", "slug", "description")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(ActivationCode)
class ActivationCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "plan", "days", "used_count", "max_uses", "is_active", "expires_at", "usable")
    list_filter = ("plan", "is_active")
    search_fields = ("code",)
    readonly_fields = ("used_count", "created_at")
