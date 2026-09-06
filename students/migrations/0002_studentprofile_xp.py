from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("students", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="studentprofile",
            name="xp",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddIndex(
            model_name="studentprofile",
            index=models.Index(fields=["xp"], name="students_stu_xp_8d4f7b_idx"),
        ),
    ]
