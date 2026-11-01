from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        # Run after the existing exams migration branches have been merged.
        ("exams", "0007_rename_exams_place_answer__b2b8b1_idx_exams_place_answer__14142a_idx_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="placementquestion",
            name="text",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="placementquestion",
            name="option_a",
            field=models.CharField(blank=True, default="", max_length=300),
        ),
        migrations.AlterField(
            model_name="placementquestion",
            name="option_b",
            field=models.CharField(blank=True, default="", max_length=300),
        ),
        migrations.AlterField(
            model_name="placementquestion",
            name="option_c",
            field=models.CharField(blank=True, default="", max_length=300),
        ),
        migrations.AlterField(
            model_name="placementquestion",
            name="option_d",
            field=models.CharField(blank=True, default="", max_length=300),
        ),
        migrations.AddField(
            model_name="placementquestion",
            name="question_image",
            field=models.ImageField(blank=True, upload_to="exam_questions/questions/"),
        ),
        migrations.AddField(
            model_name="placementquestion",
            name="option_a_image",
            field=models.ImageField(blank=True, upload_to="exam_questions/options/"),
        ),
        migrations.AddField(
            model_name="placementquestion",
            name="option_b_image",
            field=models.ImageField(blank=True, upload_to="exam_questions/options/"),
        ),
        migrations.AddField(
            model_name="placementquestion",
            name="option_c_image",
            field=models.ImageField(blank=True, upload_to="exam_questions/options/"),
        ),
        migrations.AddField(
            model_name="placementquestion",
            name="option_d_image",
            field=models.ImageField(blank=True, upload_to="exam_questions/options/"),
        ),
    ]
