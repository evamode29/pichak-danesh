from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class Product(models.Model):
    class ProductType(models.TextChoices):
        SUBSCRIPTION = "subscription", "اشتراک"
        CONTENT = "content", "بسته آموزشی"

    title = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True)
    description = models.TextField(blank=True)
    product_type = models.CharField(max_length=20, choices=ProductType.choices, default=ProductType.CONTENT)
    price = models.PositiveIntegerField(default=0, help_text="قیمت به تومان")
    is_free = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_free", "price", "-id"]

    def __str__(self):
        return self.title


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    duration_days = models.PositiveIntegerField(default=30)
    price = models.PositiveIntegerField(default=0, help_text="قیمت به تومان")
    is_active = models.BooleanField(default=True)
    product = models.OneToOneField(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name="subscription_plan")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["price", "duration_days", "id"]

    def __str__(self):
        return self.name


class Purchase(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار پرداخت"
        PAID = "paid", "پرداخت شده"
        CANCELLED = "cancelled", "لغو شده"
        GIFT = "gift", "هدیه / دستی"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="purchases")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="purchases")
    amount = models.PositiveIntegerField(default=0, help_text="مبلغ به تومان")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reference = models.CharField(max_length=120, blank=True)
    authority = models.CharField(max_length=120, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["user", "status", "-created_at"]),
            models.Index(fields=["product", "status"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.product}"


class Subscription(models.Model):
    class Source(models.TextChoices):
        PURCHASE = "purchase", "خرید"
        ADMIN = "admin", "فعال‌سازی مدیر"
        ACTIVATION = "activation", "کد فعال‌سازی"
        SCHOOL = "school", "مدرسه / هدیه"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, related_name="subscriptions")
    starts_at = models.DateTimeField(default=timezone.now)
    ends_at = models.DateTimeField()
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.ADMIN)
    purchase = models.OneToOneField(Purchase, on_delete=models.SET_NULL, null=True, blank=True, related_name="subscription")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-ends_at", "-id"]
        indexes = [models.Index(fields=["user", "is_active", "-ends_at"])]

    def __str__(self):
        return f"{self.user} - {self.plan}"

    @property
    def active_now(self):
        return self.is_active and self.ends_at >= timezone.now()

    @classmethod
    def active_for(cls, user):
        return cls.objects.filter(user=user, is_active=True, ends_at__gte=timezone.now()).select_related("plan").order_by("-ends_at").first()

    def extend_from_now(self, days):
        base = max(self.ends_at, timezone.now())
        self.ends_at = base + timedelta(days=days)
        self.save(update_fields=["ends_at"])


class Content(models.Model):
    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    body = models.TextField(blank=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="contents")
    is_free = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return self.title

    def has_access(self, user):
        if not user.is_authenticated:
            return self.is_free
        if self.is_free or user.is_staff or user.is_superuser:
            return True
        if Subscription.active_for(user):
            return True
        return self.product.purchases.filter(user=user, status__in=[Purchase.Status.PAID, Purchase.Status.GIFT]).exists()


class ActivationCode(models.Model):
    code = models.CharField(max_length=40, unique=True)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, related_name="activation_codes")
    days = models.PositiveIntegerField(default=30)
    max_uses = models.PositiveIntegerField(default=1)
    used_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return self.code

    @property
    def usable(self):
        return self.is_active and self.used_count < self.max_uses and (not self.expires_at or self.expires_at >= timezone.now())
