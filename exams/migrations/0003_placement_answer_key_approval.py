from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("exams", "0002_seed_grade6_diagnostic"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="placementattempt",
            name="answer_key_published",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="placementattempt",
            name="approved_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="placementattempt",
            name="approved_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="approved_placement_attempts",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddIndex(
            model_name="placementattempt",
            index=models.Index(fields=["answer_key_published", "-completed_at"], name="exams_place_answer__b2b8b1_idx"),
        ),
    ]
