from django.db import migrations


def seed_plans(apps, schema_editor):
    Product = apps.get_model("subscriptions", "Product")
    SubscriptionPlan = apps.get_model("subscriptions", "SubscriptionPlan")

    plans = [
        ("اشتراک ماهانه", "monthly", "دسترسی کامل به محتوای ویژه پیچک دانش برای ۳۰ روز.", 30, 99000),
        ("اشتراک سه‌ماهه", "quarterly", "سه ماه یادگیری هدفمند با دسترسی کامل به محتوای ویژه.", 90, 249000),
        ("اشتراک سالانه", "yearly", "یک سال دسترسی کامل برای مسیر یادگیری ششم.", 365, 699000),
    ]
    for name, slug, description, days, price in plans:
        product, _ = Product.objects.update_or_create(
            slug=f"subscription-{slug}",
            defaults={
                "title": name,
                "description": description,
                "product_type": "subscription",
                "price": price,
                "is_free": False,
                "is_active": True,
            },
        )
        SubscriptionPlan.objects.update_or_create(
            slug=slug,
            defaults={
                "name": name,
                "description": description,
                "duration_days": days,
                "price": price,
                "is_active": True,
                "product": product,
            },
        )


def remove_plans(apps, schema_editor):
    SubscriptionPlan = apps.get_model("subscriptions", "SubscriptionPlan")
    Product = apps.get_model("subscriptions", "Product")
    SubscriptionPlan.objects.filter(slug__in=["monthly", "quarterly", "yearly"]).delete()
    Product.objects.filter(slug__in=["subscription-monthly", "subscription-quarterly", "subscription-yearly"]).delete()


class Migration(migrations.Migration):
    dependencies = [("subscriptions", "0001_initial")]
    operations = [migrations.RunPython(seed_plans, remove_plans)]
