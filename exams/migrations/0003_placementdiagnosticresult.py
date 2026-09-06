from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("exams", "0002_seed_grade6_diagnostic"),
    ]

    operations = [
        migrations.CreateModel(
            name="PlacementDiagnosticResult",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("subject", models.CharField(choices=[("math", "ریاضی"), ("science", "علوم"), ("persian", "فارسی"), ("social", "مطالعات اجتماعی")], max_length=20)),
                ("topic", models.CharField(blank=True, default="", max_length=100)),
                ("skill", models.CharField(blank=True, default="", max_length=120)),
                ("correct_answers", models.PositiveSmallIntegerField(default=0)),
                ("total_questions", models.PositiveSmallIntegerField(default=0)),
                ("percentage", models.PositiveSmallIntegerField(default=0)),
                ("attempt", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="diagnostic_results", to="exams.placementattempt")),
            ],
            options={
                "ordering": ["subject", "topic", "skill", "id"],
            },
        ),
        migrations.AddIndex(
            model_name="placementdiagnosticresult",
            index=models.Index(fields=["attempt", "subject"], name="exams_place_attempt__idx"),
        ),
        migrations.AddIndex(
            model_name="placementdiagnosticresult",
            index=models.Index(fields=["subject", "topic", "skill"], name="exams_place_subject__idx"),
        ),
    ]
