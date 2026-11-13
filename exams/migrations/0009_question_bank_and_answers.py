# Generated for the reusable question bank.
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("exams", "0008_merge_20261111_0144"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="QuestionCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("subject", models.CharField(choices=[("math", "ریاضی"), ("science", "علوم"), ("persian", "فارسی"), ("social", "مطالعات اجتماعی")], max_length=20)),
                ("grade", models.PositiveSmallIntegerField(default=6)),
                ("sort_order", models.PositiveSmallIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("parent", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="children", to="exams.questioncategory")),
            ],
            options={"ordering": ["subject", "grade", "sort_order", "name"]},
        ),
        migrations.CreateModel(
            name="BankQuestion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("subject", models.CharField(choices=[("math", "ریاضی"), ("science", "علوم"), ("persian", "فارسی"), ("social", "مطالعات اجتماعی")], default="math", max_length=20)),
                ("grade", models.PositiveSmallIntegerField(default=6)),
                ("text", models.TextField()),
                ("question_image", models.ImageField(blank=True, upload_to="question_bank/questions/")),
                ("option_a", models.CharField(blank=True, default="", max_length=300)),
                ("option_a_image", models.ImageField(blank=True, upload_to="question_bank/options/")),
                ("option_b", models.CharField(blank=True, default="", max_length=300)),
                ("option_b_image", models.ImageField(blank=True, upload_to="question_bank/options/")),
                ("option_c", models.CharField(blank=True, default="", max_length=300)),
                ("option_c_image", models.ImageField(blank=True, upload_to="question_bank/options/")),
                ("option_d", models.CharField(blank=True, default="", max_length=300)),
                ("option_d_image", models.ImageField(blank=True, upload_to="question_bank/options/")),
                ("correct_option", models.CharField(choices=[("A", "گزینه ۱"), ("B", "گزینه ۲"), ("C", "گزینه ۳"), ("D", "گزینه ۴")], max_length=1)),
                ("difficulty", models.PositiveSmallIntegerField(default=2)),
                ("explanation", models.TextField(blank=True, default="")),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("categories", models.ManyToManyField(blank=True, related_name="questions", to="exams.questioncategory")),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_bank_questions", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["subject", "grade", "-created_at", "-id"]},
        ),
        migrations.CreateModel(
            name="TestBankQuestion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("order", models.PositiveSmallIntegerField(default=1)),
                ("is_active", models.BooleanField(default=True)),
                ("question", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="test_links", to="exams.bankquestion")),
                ("test", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="bank_links", to="exams.placementtest")),
            ],
            options={"ordering": ["order", "id"]},
        ),
        migrations.CreateModel(
            name="PlacementAnswer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("question_text", models.TextField()),
                ("selected_option", models.CharField(choices=[("A", "گزینه ۱"), ("B", "گزینه ۲"), ("C", "گزینه ۳"), ("D", "گزینه ۴")], max_length=1)),
                ("correct_option", models.CharField(choices=[("A", "گزینه ۱"), ("B", "گزینه ۲"), ("C", "گزینه ۳"), ("D", "گزینه ۴")], max_length=1)),
                ("is_correct", models.BooleanField(default=False)),
                ("subject", models.CharField(choices=[("math", "ریاضی"), ("science", "علوم"), ("persian", "فارسی"), ("social", "مطالعات اجتماعی")], max_length=20)),
                ("topic", models.CharField(blank=True, default="", max_length=100)),
                ("skill", models.CharField(blank=True, default="", max_length=120)),
                ("category_names", models.JSONField(blank=True, default=list)),
                ("answered_at", models.DateTimeField(auto_now_add=True)),
                ("attempt", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="answers", to="exams.placementattempt")),
                ("bank_question", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="student_answers", to="exams.bankquestion")),
                ("legacy_question", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="student_answers", to="exams.placementquestion")),
            ],
            options={"ordering": ["id"]},
        ),
        migrations.AddConstraint(
            model_name="questioncategory",
            constraint=models.UniqueConstraint(fields=("parent", "name", "subject", "grade"), name="qcat_parent_name_subj_grade_uq"),
        ),
        migrations.AddIndex(
            model_name="questioncategory",
            index=models.Index(fields=["subject", "grade", "is_active"], name="qcat_subj_grade_active_idx"),
        ),
        migrations.AddIndex(
            model_name="bankquestion",
            index=models.Index(fields=["subject", "grade", "is_active"], name="bankq_subj_grade_active_idx"),
        ),
        migrations.AddIndex(
            model_name="bankquestion",
            index=models.Index(fields=["difficulty", "is_active"], name="bankq_diff_active_idx"),
        ),
        migrations.AddConstraint(
            model_name="testbankquestion",
            constraint=models.UniqueConstraint(fields=("test", "question"), name="exams_test_bank_question_uniq"),
        ),
        migrations.AddIndex(
            model_name="testbankquestion",
            index=models.Index(fields=["test", "is_active", "order"], name="test_bank_active_order_idx"),
        ),
        migrations.AddIndex(
            model_name="placementanswer",
            index=models.Index(fields=["attempt", "is_correct"], name="answer_attempt_correct_idx"),
        ),
        migrations.AddIndex(
            model_name="placementanswer",
            index=models.Index(fields=["subject", "topic", "skill"], name="answer_subj_topic_skill_idx"),
        ),
    ]
