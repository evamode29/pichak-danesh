from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("subscriptions", "0002_seed_subscription_plans"),
    ]

    operations = [
        migrations.AddField(
            model_name="purchase",
            name="authority",
            field=models.CharField(blank=True, db_index=True, max_length=120),
        ),
    ]
