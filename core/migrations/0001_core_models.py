from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(choices=[("student", "دانش‌آموز"), ("teacher", "معلم"), ("parent", "والد"), ("admin", "مدیر")], default="student", max_length=20)),
                ("mobile", models.CharField(blank=True, max_length=15, null=True, unique=True)),
                ("display_name", models.CharField(blank=True, max_length=120)),
                ("is_active_profile", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="profile", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["id"]},
        ),
        migrations.CreateModel(
            name="ClassRoom",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("grade", models.PositiveSmallIntegerField(default=6)),
                ("academic_year", models.CharField(blank=True, max_length=20)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("teacher", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="teaching_classes", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["grade", "name"]},
        ),
        migrations.AddIndex(model_name="classroom", index=models.Index(fields=["grade", "is_active"], name="core_classr_grade_i_2a4d25_idx")),
        migrations.AddIndex(model_name="classroom", index=models.Index(fields=["teacher", "is_active"], name="core_classr_teacher_6c3b3b_idx")),
    ]
