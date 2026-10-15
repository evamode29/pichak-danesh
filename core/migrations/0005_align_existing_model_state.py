from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0004_merge_20260914"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameIndex(
            model_name="dailytask",
            old_name="core_dailyt_classroo_6f1c35_idx",
            new_name="core_dailyt_classro_5e6a17_idx",
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="role",
            field=models.CharField(
                choices=[
                    ("student", "دانش‌آموز"),
                    ("teacher", "معلم"),
                    ("parent", "والد"),
                    ("admin", "مدیر اصلی"),
                    ("content_manager", "مدیر محتوا"),
                ],
                default="student",
                max_length=20,
            ),
        ),
    ]
