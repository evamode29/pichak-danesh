from django.conf import settings
from django.db import models


class PlacementTest(models.Model):
    title = models.CharField(max_length=160, default="آزمون تعیین سطح پایه ششم")
    grade = models.PositiveSmallIntegerField(default=6)
    duration_minutes = models.PositiveSmallIntegerField(default=15)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.title


class PlacementQuestion(models.Model):
    class Subject(models.TextChoices):
        MATH = "math", "ریاضی"
        SCIENCE = "science", "علوم"
        PERSIAN = "persian", "فارسی"
        SOCIAL = "social", "مطالعات اجتماعی"

    class Option(models.TextChoices):
        A = "A", "گزینه ۱"
        B = "B", "گزینه ۲"
        C = "C", "گزینه ۳"
        D = "D", "گزینه ۴"

    test = models.ForeignKey(PlacementTest, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField(blank=True, default="")
    question_image = models.ImageField(upload_to="exam_questions/questions/", blank=True)
    option_a = models.CharField(max_length=300, blank=True, default="")
    option_a_image = models.ImageField(upload_to="exam_questions/options/", blank=True)
    option_b = models.CharField(max_length=300, blank=True, default="")
    option_b_image = models.ImageField(upload_to="exam_questions/options/", blank=True)
    option_c = models.CharField(max_length=300, blank=True, default="")
    option_c_image = models.ImageField(upload_to="exam_questions/options/", blank=True)
    option_d = models.CharField(max_length=300, blank=True, default="")
    option_d_image = models.ImageField(upload_to="exam_questions/options/", blank=True)
    correct_option = models.CharField(max_length=1, choices=Option.choices)
    subject = models.CharField(max_length=20, choices=Subject.choices, default=Subject.MATH)
    topic = models.CharField(max_length=100, blank=True, default="")
    skill = models.CharField(max_length=120, blank=True, default="")
    difficulty = models.PositiveSmallIntegerField(default=2)
    order = models.PositiveSmallIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        indexes = [
            models.Index(fields=["test", "is_active", "order"]),
            models.Index(fields=["subject", "difficulty"]),
            models.Index(fields=["subject", "topic", "skill"]),
        ]

    def __str__(self):
        return f"{self.test.title} - {self.order}"


class PlacementAttempt(models.Model):
    student = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="placement_attempts")
    test = models.ForeignKey(PlacementTest, on_delete=models.CASCADE, related_name="attempts")
    score = models.PositiveSmallIntegerField(default=0)
    correct_answers = models.PositiveSmallIntegerField(default=0)
    total_questions = models.PositiveSmallIntegerField(default=0)
    level = models.PositiveSmallIntegerField(default=1)
    answer_key_published = models.BooleanField(default=False)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_placement_attempts")
    approved_at = models.DateTimeField(null=True, blank=True)
    repeat_requested = models.BooleanField(default=False)
    repeat_approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_placement_repeats")
    repeat_approved_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-completed_at", "-id"]
        indexes = [
            models.Index(fields=["student", "-completed_at"]),
            models.Index(fields=["answer_key_published", "-completed_at"]),
            models.Index(fields=["student", "repeat_requested", "-completed_at"]),
        ]

    def __str__(self):
        return f"{self.student} - سطح {self.level}"


class PlacementDiagnosticResult(models.Model):
    attempt = models.ForeignKey(PlacementAttempt, on_delete=models.CASCADE, related_name="diagnostic_results")
    subject = models.CharField(max_length=20, choices=PlacementQuestion.Subject.choices)
    topic = models.CharField(max_length=100, blank=True, default="")
    skill = models.CharField(max_length=120, blank=True, default="")
    correct_answers = models.PositiveSmallIntegerField(default=0)
    total_questions = models.PositiveSmallIntegerField(default=0)
    percentage = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["subject", "topic", "skill", "id"]
        indexes = [models.Index(fields=["attempt", "subject"]), models.Index(fields=["subject", "topic", "skill"])]

    def __str__(self):
        return f"{self.attempt} - {self.get_subject_display()} - {self.topic}"



class QuestionCategory(models.Model):
    """Hierarchical curriculum category used to classify reusable bank questions."""

    name = models.CharField(max_length=120)
    subject = models.CharField(max_length=20, choices=PlacementQuestion.Subject.choices)
    grade = models.PositiveSmallIntegerField(default=6)
    parent = models.ForeignKey(
        "self", on_delete=models.PROTECT, null=True, blank=True,
        related_name="children",
    )
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["subject", "grade", "sort_order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["parent", "name", "subject", "grade"],
                name="qcat_parent_name_subj_grade_uq",
            )
        ]
        indexes = [models.Index(fields=["subject", "grade", "is_active"])]

    def __str__(self):
        return self.name


class BankQuestion(models.Model):
    """Reusable question, independent from any particular test."""

    class Option(models.TextChoices):
        A = "A", "گزینه ۱"
        B = "B", "گزینه ۲"
        C = "C", "گزینه ۳"
        D = "D", "گزینه ۴"

    subject = models.CharField(
        max_length=20, choices=PlacementQuestion.Subject.choices,
        default=PlacementQuestion.Subject.MATH,
    )
    grade = models.PositiveSmallIntegerField(default=6)
    text = models.TextField()
    question_image = models.ImageField(upload_to="question_bank/questions/", blank=True)
    option_a = models.CharField(max_length=300, blank=True, default="")
    option_a_image = models.ImageField(upload_to="question_bank/options/", blank=True)
    option_b = models.CharField(max_length=300, blank=True, default="")
    option_b_image = models.ImageField(upload_to="question_bank/options/", blank=True)
    option_c = models.CharField(max_length=300, blank=True, default="")
    option_c_image = models.ImageField(upload_to="question_bank/options/", blank=True)
    option_d = models.CharField(max_length=300, blank=True, default="")
    option_d_image = models.ImageField(upload_to="question_bank/options/", blank=True)
    correct_option = models.CharField(max_length=1, choices=Option.choices)
    difficulty = models.PositiveSmallIntegerField(default=2)
    explanation = models.TextField(blank=True, default="")
    categories = models.ManyToManyField(
        QuestionCategory, blank=True, related_name="questions"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="created_bank_questions",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["subject", "grade", "-created_at", "-id"]
        indexes = [
            models.Index(fields=["subject", "grade", "is_active"]),
            models.Index(fields=["difficulty", "is_active"]),
        ]

    def __str__(self):
        return self.text[:90]


class TestBankQuestion(models.Model):
    """Connects reusable bank questions to a test without copying question data."""

    test = models.ForeignKey(
        PlacementTest, on_delete=models.CASCADE, related_name="bank_links"
    )
    question = models.ForeignKey(
        BankQuestion, on_delete=models.PROTECT, related_name="test_links"
    )
    order = models.PositiveSmallIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["test", "question"], name="exams_test_bank_question_uniq"
            )
        ]
        indexes = [models.Index(fields=["test", "is_active", "order"])]

    def __str__(self):
        return f"{self.test.title} - {self.question_id}"


class PlacementAnswer(models.Model):
    """Immutable per-question answer snapshot for a completed attempt."""

    attempt = models.ForeignKey(
        PlacementAttempt, on_delete=models.CASCADE, related_name="answers"
    )
    bank_question = models.ForeignKey(
        BankQuestion, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="student_answers",
    )
    legacy_question = models.ForeignKey(
        PlacementQuestion, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="student_answers",
    )
    question_text = models.TextField()
    selected_option = models.CharField(max_length=1, choices=BankQuestion.Option.choices)
    correct_option = models.CharField(max_length=1, choices=BankQuestion.Option.choices)
    is_correct = models.BooleanField(default=False)
    subject = models.CharField(max_length=20, choices=PlacementQuestion.Subject.choices)
    topic = models.CharField(max_length=100, blank=True, default="")
    skill = models.CharField(max_length=120, blank=True, default="")
    category_names = models.JSONField(default=list, blank=True)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]
        indexes = [
            models.Index(fields=["attempt", "is_correct"]),
            models.Index(fields=["subject", "topic", "skill"]),
        ]

    def __str__(self):
        return f"{self.attempt_id} - {self.selected_option}"
