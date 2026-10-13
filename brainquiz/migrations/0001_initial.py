from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [("students", "0001_initial")]
    operations = [migrations.CreateModel(name="BrainQuizAttempt", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("score", models.PositiveSmallIntegerField(default=0)), ("correct_answers", models.PositiveSmallIntegerField(default=0)), ("total_questions", models.PositiveSmallIntegerField(default=20)), ("duration_seconds", models.PositiveIntegerField(default=0)), ("answers", models.JSONField(blank=True, default=dict)), ("completed_at", models.DateTimeField(auto_now_add=True)), ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="brain_quiz_attempts", to="students.studentprofile"))], options={"ordering": ["-completed_at", "-id"]})]
