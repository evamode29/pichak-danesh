# Generated manually for the expanded student record.

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0007_student_attendance_family_contact"),
        ("students", "0005_merge_20260918_mobile_xp"),
    ]

    operations = [
        migrations.CreateModel(
            name="StudentStudySession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("session_date", models.DateField()),
                ("subject", models.CharField(blank=True, max_length=50)),
                ("topic", models.CharField(blank=True, max_length=150)),
                ("minutes", models.PositiveIntegerField(default=0)),
                ("questions_count", models.PositiveIntegerField(default=0)),
                ("correct_count", models.PositiveIntegerField(default=0)),
                ("completion", models.PositiveSmallIntegerField(default=100)),
                ("note", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="study_sessions", to="students.studentprofile")),
                ("teacher", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="student_study_sessions", to="auth.user")),
            ],
            options={"ordering": ["-session_date", "-id"], "indexes": [models.Index(fields=["student", "-session_date"], name="core_studen_student_5e4c7d_idx")]},
        ),
        migrations.CreateModel(
            name="StudentBehaviorObservation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("observation_date", models.DateField()),
                ("observation_type", models.CharField(choices=[("positive", "نقطه قوت"), ("challenge", "نیازمند پیگیری")], default="positive", max_length=20)),
                ("area", models.CharField(blank=True, max_length=80)),
                ("observation", models.TextField()),
                ("action_taken", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="behavior_observations", to="students.studentprofile")),
                ("teacher", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="student_behavior_observations", to="auth.user")),
            ],
            options={"ordering": ["-observation_date", "-id"], "indexes": [models.Index(fields=["student", "-observation_date"], name="core_studen_student_3d5b58_idx")]},
        ),
        migrations.CreateModel(
            name="StudentPortfolioItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("item_date", models.DateField()),
                ("subject", models.CharField(blank=True, max_length=50)),
                ("description", models.TextField(blank=True)),
                ("file", models.FileField(blank=True, null=True, upload_to="student_portfolio/%Y/%m/")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="portfolio_items", to="students.studentprofile")),
                ("teacher", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="student_portfolio_items", to="auth.user")),
            ],
            options={"ordering": ["-item_date", "-id"], "indexes": [models.Index(fields=["student", "-item_date"], name="core_studen_student_0d8e67_idx")]},
        ),
        migrations.CreateModel(
            name="StudentAnnualReview",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("academic_year", models.CharField(max_length=20)),
                ("period", models.CharField(choices=[("start", "ابتدای سال"), ("mid", "میان‌سال"), ("end", "پایان سال")], max_length=10)),
                ("review_date", models.DateField()),
                ("academic_summary", models.TextField(blank=True)),
                ("strengths", models.TextField(blank=True)),
                ("needs_improvement", models.TextField(blank=True)),
                ("next_steps", models.TextField(blank=True)),
                ("parent_message", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="annual_reviews", to="students.studentprofile")),
                ("teacher", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="student_annual_reviews", to="auth.user")),
            ],
            options={"ordering": ["-review_date", "-id"], "indexes": [models.Index(fields=["student", "-review_date"], name="core_studen_student_4d7e0c_idx")]},
        ),
        migrations.AddConstraint(
            model_name="studentannualreview",
            constraint=models.UniqueConstraint(fields=("student", "academic_year", "period"), name="unique_student_annual_review_period"),
        ),
    ]
