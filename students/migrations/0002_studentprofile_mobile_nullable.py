from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("students", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="studentprofile",
            name="mobile",
            field=models.CharField(blank=True, max_length=15, null=True, unique=True),
        ),
    ]
