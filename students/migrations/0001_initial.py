from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("core", "0001_core_models"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="StudentProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("mobile", models.CharField(max_length=15, unique=True)),
                ("grade", models.PositiveSmallIntegerField(default=6)),
                ("is_free", models.BooleanField(default=True)),
                ("points", models.PositiveIntegerField(default=0)),
                ("level", models.PositiveIntegerField(default=1)),
                ("streak", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("classroom", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="students", to="core.classroom")),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="student_profile", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-points", "id"]},
        ),
        migrations.CreateModel(
            name="ParentProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("mobile", models.CharField(max_length=15, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="parent_profile", to=settings.AUTH_USER_MODEL)),
                ("students", models.ManyToManyField(blank=True, related_name="parents", to="students.studentprofile")),
            ],
        ),
        migrations.AddIndex(model_name="studentprofile", index=models.Index(fields=["grade", "classroom"], name="students_stu_grade_c4f7d5_idx")),
        migrations.AddIndex(model_name="studentprofile", index=models.Index(fields=["points"], name="students_stu_points_7c3b8f_idx")),
    ]
