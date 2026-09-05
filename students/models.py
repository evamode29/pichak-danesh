from django.contrib.auth import get_user_model
from django.db import models

from core.models import ClassRoom


User = get_user_model()


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    classroom = models.ForeignKey(
        ClassRoom,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
    )
    mobile = models.CharField(max_length=15, unique=True)
    grade = models.PositiveSmallIntegerField(default=6)
    is_free = models.BooleanField(default=True)
    points = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    streak = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-points", "id"]
        indexes = [
            models.Index(fields=["grade", "classroom"]),
            models.Index(fields=["points"]),
        ]

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class ParentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="parent_profile")
    mobile = models.CharField(max_length=15, unique=True)
    students = models.ManyToManyField(StudentProfile, related_name="parents", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username
