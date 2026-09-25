from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0004_merge_20260914"),
    ]

    operations = [
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
]
