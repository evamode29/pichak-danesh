from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0004_merge_20260914"),
        ("students", "0005_merge_20260918_mobile_xp"),
    ]

    operations = [
        migrations.CreateModel(
            name="TeacherStudentNote",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("kind", models.CharField(choices=[("note", "یادداشت معلم"), ("feedback", "بازخورد"), ("ai_analysis", "تحلیل هوش مصنوعی")], default="note", max_length=20)),
                ("title", models.CharField(blank=True, max_length=200)),
                ("content", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="teacher_notes", to="students.studentprofile")),
                ("teacher", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="student_notes", to="auth.user")),
            ],
            options={"ordering": ["-created_at", "-id"], "indexes": [models.Index(fields=["student", "kind", "-created_at"], name="core_teache_student_8f5e8d_idx")]},
        ),
    ]
