from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0006_student_educational_assessment_student_goal"),
        ("students", "0005_merge_20260918_mobile_xp"),
    ]

    operations = [
        migrations.CreateModel(
            name="StudentAttendance",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField()),
                ("status", models.CharField(choices=[("present", "حاضر"), ("absent", "غایب"), ("late", "با تأخیر")], default="present", max_length=20)),
                ("mood", models.CharField(blank=True, choices=[("great", "خیلی خوب"), ("good", "خوب"), ("normal", "عادی"), ("low", "کم‌انرژی")], max_length=20)),
                ("note", models.CharField(blank=True, max_length=500)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attendance_records", to="students.studentprofile")),
                ("teacher", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="student_attendance_records", to="auth.user")),
            ],
            options={"ordering": ["-date", "-id"], "indexes": [models.Index(fields=["student", "-date"], name="core_studen_student_0e4a5f_idx")]},
        ),
        migrations.CreateModel(
            name="StudentFamilyContact",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("contact_date", models.DateField()),
                ("kind", models.CharField(choices=[("call", "تماس"), ("meeting", "جلسه"), ("message", "پیام"), ("followup", "پیگیری")], default="call", max_length=20)),
                ("summary", models.TextField()),
                ("follow_up", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="family_contacts", to="students.studentprofile")),
                ("teacher", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="student_family_contacts", to="auth.user")),
            ],
            options={"ordering": ["-contact_date", "-id"], "indexes": [models.Index(fields=["student", "-contact_date"], name="core_studen_student_7db9d8_idx")]},
        ),
        migrations.AddConstraint(
            model_name="studentattendance",
            constraint=models.UniqueConstraint(fields=("student", "date"), name="unique_student_attendance_date"),
        ),
    ]
