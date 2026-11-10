from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import core.storage


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0005_align_existing_model_state"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="dailytask",
            name="instruction_file",
            field=models.FileField(blank=True, upload_to="homework/instructions/%Y/%m/", storage=core.storage.PrivateHomeworkStorage()),
        ),
        migrations.AlterField(
            model_name="studenttask",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "انجام نشده"),
                    ("done", "انجام شد"),
                    ("review", "در انتظار بررسی"),
                    ("returned", "نیاز به اصلاح"),
                ],
                default="pending",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="studenttask",
            name="answer_text",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="studenttask",
            name="attachment",
            field=models.FileField(blank=True, upload_to="homework/submissions/%Y/%m/", storage=core.storage.PrivateHomeworkStorage()),
        ),
        migrations.AddField(
            model_name="studenttask",
            name="submitted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="studenttask",
            name="reviewed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="studenttask",
            name="reviewed_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="reviewed_student_tasks",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
