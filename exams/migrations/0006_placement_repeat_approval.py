from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("exams", "0005_merge_diagnostic_migrations"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="placementattempt",
            name="repeat_requested",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="placementattempt",
            name="repeat_approved_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="approved_placement_repeats",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="placementattempt",
            name="repeat_approved_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddIndex(
            model_name="placementattempt",
            index=models.Index(fields=["student", "repeat_requested", "-completed_at"], name="exams_place_student_2b8c4e_idx"),
        ),
    ]
