from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=160)),
                ("slug", models.SlugField(max_length=180, unique=True)),
                ("description", models.TextField(blank=True)),
                ("product_type", models.CharField(choices=[("subscription", "اشتراک"), ("content", "بسته آموزشی")], default="content", max_length=20)),
                ("price", models.PositiveIntegerField(default=0, help_text="قیمت به تومان")),
                ("is_free", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["-is_free", "price", "-id"]},
        ),
        migrations.CreateModel(
            name="SubscriptionPlan",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("slug", models.SlugField(max_length=140, unique=True)),
                ("description", models.TextField(blank=True)),
                ("duration_days", models.PositiveIntegerField(default=30)),
                ("price", models.PositiveIntegerField(default=0, help_text="قیمت به تومان")),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("product", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="subscription_plan", to="subscriptions.product")),
            ],
            options={"ordering": ["price", "duration_days", "id"]},
        ),
        migrations.CreateModel(
            name="Purchase",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount", models.PositiveIntegerField(default=0, help_text="مبلغ به تومان")),
                ("status", models.CharField(choices=[("pending", "در انتظار پرداخت"), ("paid", "پرداخت شده"), ("cancelled", "لغو شده"), ("gift", "هدیه / دستی")], default="pending", max_length=20)),
                ("reference", models.CharField(blank=True, max_length=120)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("paid_at", models.DateTimeField(blank=True, null=True)),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="purchases", to="subscriptions.product")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="purchases", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at", "-id"]},
        ),
        migrations.CreateModel(
            name="Subscription",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("starts_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("ends_at", models.DateTimeField()),
                ("source", models.CharField(choices=[("purchase", "خرید"), ("admin", "فعال‌سازی مدیر"), ("activation", "کد فعال‌سازی"), ("school", "مدرسه / هدیه")], default="admin", max_length=20)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("plan", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="subscriptions", to="subscriptions.subscriptionplan")),
                ("purchase", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="subscription", to="subscriptions.purchase")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="subscriptions", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-ends_at", "-id"]},
        ),
        migrations.CreateModel(
            name="Content",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=180)),
                ("slug", models.SlugField(max_length=200, unique=True)),
                ("description", models.TextField(blank=True)),
                ("body", models.TextField(blank=True)),
                ("is_free", models.BooleanField(default=False)),
                ("is_published", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="contents", to="subscriptions.product")),
            ],
            options={"ordering": ["-created_at", "-id"]},
        ),
        migrations.CreateModel(
            name="ActivationCode",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=40, unique=True)),
                ("days", models.PositiveIntegerField(default=30)),
                ("max_uses", models.PositiveIntegerField(default=1)),
                ("used_count", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("plan", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="activation_codes", to="subscriptions.subscriptionplan")),
            ],
            options={"ordering": ["-created_at", "-id"]},
        ),
        migrations.AddIndex(model_name="purchase", index=models.Index(fields=["user", "status", "-created_at"], name="subscriptio_user_id_8d0b36_idx")),
        migrations.AddIndex(model_name="purchase", index=models.Index(fields=["product", "status"], name="subscriptio_product_7d0e5b_idx")),
        migrations.AddIndex(model_name="subscription", index=models.Index(fields=["user", "is_active", "-ends_at"], name="subscriptio_user_id_6a6bb4_idx")),
    ]
