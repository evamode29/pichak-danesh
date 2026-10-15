from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("exams", "0004_seed_diagnostic_topics"),
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
