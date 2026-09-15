from django.db import migrations


TEACHER_USERNAME = "teacher"
TEACHER_PASSWORD_HASH = "pbkdf2_sha256$1000000$tR3um-MKnCowQA8dObquBA$kJF0r8NoAGu7pnJewYBp4gYvPZBc1GTXDyoGyFZ/OJk="


def create_teacher(apps, schema_editor):
    User = apps.get_model("auth", "User")
    UserProfile = apps.get_model("core", "UserProfile")

    user, created = User.objects.get_or_create(
        username=TEACHER_USERNAME,
        defaults={
            "first_name": "معلم",
            "last_name": "پیچک دانش",
            "is_active": True,
        },
    )

    if created or not user.has_usable_password():
        user.password = TEACHER_PASSWORD_HASH
        user.save(update_fields=["password"])

    UserProfile.objects.update_or_create(
        user_id=user.id,
        defaults={
            "role": "teacher",
            "display_name": "معلم پیچک دانش",
            "is_active_profile": True,
        },
    )


def reverse_teacher(apps, schema_editor):
    User = apps.get_model("auth", "User")
    User.objects.filter(username=TEACHER_USERNAME).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_daily_tasks"),
    ]

    operations = [
        migrations.RunPython(create_teacher, reverse_teacher),
    ]
