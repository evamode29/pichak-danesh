from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0005_teacher_student_note"),
        ("students", "0005_merge_20260918_mobile_xp"),
    ]

    operations = [
        migrations.CreateModel(
            name="StudentEducationalAssessment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("assessment_date", models.DateField()),
                ("participation", models.PositiveSmallIntegerField(default=3)),
                ("effort", models.PositiveSmallIntegerField(default=3)),
                ("focus", models.PositiveSmallIntegerField(default=3)),
                ("independence", models.PositiveSmallIntegerField(default=3)),
                ("time_management", models.PositiveSmallIntegerField(default=3)),
                ("responsibility", models.PositiveSmallIntegerField(default=3)),
                ("cooperation", models.PositiveSmallIntegerField(default=3)),
                ("problem_solving", models.PositiveSmallIntegerField(default=3)),
                ("accuracy", models.PositiveSmallIntegerField(default=3)),
                ("perseverance", models.PositiveSmallIntegerField(default=3)),
                ("strengths", models.TextField(blank=True)),
                ("needs_improvement", models.TextField(blank=True)),
                ("teacher_summary", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="educational_assessments", to="students.studentprofile")),
                ("teacher", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="educational_assessments", to="auth.user")),
            ],
            options={
                "ordering": ["-assessment_date", "-id"],
                "indexes": [models.Index(fields=["student", "-assessment_date"], name="core_studen_student_5e0a1e_idx")],
            },
        ),
        migrations.CreateModel(
            name="StudentGoal",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("subject", models.CharField(blank=True, max_length=50)),
                ("target_date", models.DateField(blank=True, null=True)),
                ("status", models.CharField(choices=[("active", "در حال پیگیری"), ("done", "انجام شد"), ("paused", "متوقف")], default="active", max_length=20)),
                ("note", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="learning_goals", to="students.studentprofile")),
                ("teacher", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="student_goals", to="auth.user")),
            ],
            options={
                "ordering": ["status", "target_date", "-id"],
                "indexes": [models.Index(fields=["student", "status"], name="core_studen_student_8a9c0b_idx")],
            },
        ),
    ]
