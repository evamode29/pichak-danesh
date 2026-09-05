from django.db import models


class PracticeQuestion(models.Model):
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

    subject = models.CharField(max_length=20, choices=Subject.choices, default=Subject.MATH)
    text = models.TextField()
    option_a = models.CharField(max_length=300)
    option_b = models.CharField(max_length=300)
    option_c = models.CharField(max_length=300)
    option_d = models.CharField(max_length=300)
    correct_option = models.CharField(max_length=1, choices=Option.choices)
    level = models.PositiveSmallIntegerField(default=1)
    difficulty = models.PositiveSmallIntegerField(default=1)
    points = models.PositiveSmallIntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["level", "subject", "id"]
        indexes = [
            models.Index(fields=["level", "subject", "is_active"]),
            models.Index(fields=["is_active", "level"]),
        ]

    def __str__(self):
        return f"{self.get_subject_display()} - سطح {self.level} - {self.id}"


class PracticeAttempt(models.Model):
    student = models.ForeignKey(
        "students.StudentProfile", on_delete=models.CASCADE, related_name="practice_attempts"
    )
    question = models.ForeignKey(PracticeQuestion, on_delete=models.CASCADE, related_name="attempts")
    selected_option = models.CharField(max_length=1, choices=PracticeQuestion.Option.choices)
    is_correct = models.BooleanField(default=False)
    points_earned = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["student", "-created_at"]),
            models.Index(fields=["question", "is_correct"]),
        ]

    def __str__(self):
        return f"{self.student} - {self.question_id} - {self.points_earned} امتیاز"
