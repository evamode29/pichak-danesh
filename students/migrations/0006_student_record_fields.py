from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("students", "0005_merge_20260918_mobile_xp")]
    operations = [
        migrations.AddField(model_name="studentprofile", name="national_id", field=models.CharField(blank=True, max_length=20)),
        migrations.AddField(model_name="studentprofile", name="student_number", field=models.CharField(blank=True, max_length=30)),
        migrations.AddField(model_name="studentprofile", name="school_name", field=models.CharField(blank=True, max_length=150)),
        migrations.AddField(model_name="studentprofile", name="academic_year", field=models.CharField(blank=True, max_length=20)),
    ]
}