from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("exams", "0009_question_bank_and_answers"),
    ]

    operations = [
        migrations.AddField(
            model_name="placementanswer",
            name="category_paths",
            field=models.JSONField(blank=True, default=list),
        ),
    ]
