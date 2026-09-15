from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_core_models"),
        ("students", "0002_rename_students_stu_grade_c4f7d5_idx_students_st_grade_6d415c_idx_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="DailyTask",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("task_date", models.DateField()),
                ("max_score", models.PositiveSmallIntegerField(default=20)),
                ("due_time", models.TimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("classroom", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="daily_tasks", to="core.classroom")),
                ("created_by", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_daily_tasks", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-task_date", "-id"]},
        ),
        migrations.CreateModel(
            name="StudentTask",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("pending", "انجام نشده"), ("done", "انجام شد"), ("review", "نیاز به بررسی")], default="pending", max_length=20)),
                ("score", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("note", models.CharField(blank=True, max_length=500)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="task_records", to="students.studentprofile")),
                ("task", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="student_tasks", to="core.dailytask")),
            ],
            options={"ordering": ["student__user__first_name", "student__user__last_name"]},
        ),
        migrations.AddIndex(model_name="dailytask", index=models.Index(fields=["classroom", "task_date"], name="core_dailyt_classroo_6f1c35_idx")),
        migrations.AddConstraint(model_name="studenttask", constraint=models.UniqueConstraint(fields=("task", "student"), name="unique_daily_task_student")),
    ]
