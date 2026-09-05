from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("students", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PracticeQuestion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("subject", models.CharField(choices=[("math", "ریاضی"), ("science", "علوم"), ("persian", "فارسی"), ("social", "مطالعات اجتماعی")], default="math", max_length=20)),
                ("text", models.TextField()),
                ("option_a", models.CharField(max_length=300)),
                ("option_b", models.CharField(max_length=300)),
                ("option_c", models.CharField(max_length=300)),
                ("option_d", models.CharField(max_length=300)),
                ("correct_option", models.CharField(choices=[("A", "گزینه ۱"), ("B", "گزینه ۲"), ("C", "گزینه ۳"), ("D", "گزینه ۴")], max_length=1)),
                ("level", models.PositiveSmallIntegerField(default=1)),
                ("difficulty", models.PositiveSmallIntegerField(default=1)),
                ("points", models.PositiveSmallIntegerField(default=10)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["level", "subject", "id"]},
        ),
        migrations.CreateModel(
            name="PracticeAttempt",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("selected_option", models.CharField(choices=[("A", "گزینه ۱"), ("B", "گزینه ۲"), ("C", "گزینه ۳"), ("D", "گزینه ۴")], max_length=1)),
                ("is_correct", models.BooleanField(default=False)),
                ("points_earned", models.PositiveSmallIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("question", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attempts", to="practice.practicequestion")),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="practice_attempts", to="students.studentprofile")),
            ],
            options={"ordering": ["-created_at", "-id"]},
        ),
        migrations.AddIndex(model_name="practicequestion", index=models.Index(fields=["level", "subject", "is_active"], name="practice_pr_level_a1b6a6_idx")),
        migrations.AddIndex(model_name="practicequestion", index=models.Index(fields=["is_active", "level"], name="practice_pr_is_acti_4b8c7b_idx")),
        migrations.AddIndex(model_name="practiceattempt", index=models.Index(fields=["student", "-created_at"], name="practice_pr_student_3e54a4_idx")),
        migrations.AddIndex(model_name="practiceattempt", index=models.Index(fields=["question", "is_correct"], name="practice_pr_question_1a4f2b_idx")),
    ]
