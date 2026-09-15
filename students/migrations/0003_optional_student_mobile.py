from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("students", "0002_rename_students_stu_grade_c4f7d5_idx_students_st_grade_6d415c_idx_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="studentprofile",
            name="mobile",
            field=models.CharField(blank=True, max_length=15, null=True, unique=True),
        ),
    ]
