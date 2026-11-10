from django.db import migrations


def reclassify_legacy_empty_reviews(apps, schema_editor):
    """Old UI marked tasks as review without collecting an actual answer."""
    StudentTask = apps.get_model("core", "StudentTask")
    StudentTask.objects.filter(
        status="review",
        answer_text="",
        attachment="",
    ).update(status="pending", submitted_at=None, reviewed_at=None, reviewed_by=None)


class Migration(migrations.Migration):
    dependencies = [("core", "0006_homework_submissions")]

    operations = [
        migrations.RunPython(
            reclassify_legacy_empty_reviews,
            migrations.RunPython.noop,
        ),
    ]
