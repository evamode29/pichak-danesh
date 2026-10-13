from django.db import models


class BrainQuizAttempt(models.Model):
    student = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="brain_quiz_attempts")
    score = models.PositiveSmallIntegerField(default=0)
    correct_answers = models.PositiveSmallIntegerField(default=0)
    total_questions = models.PositiveSmallIntegerField(default=20)
    duration_seconds = models.PositiveIntegerField(default=0)
    answers = models.JSONField(default=dict, blank=True)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-completed_at", "-id"]

    def __str__(self):
        return f"{self.student} — {self.score}%"
