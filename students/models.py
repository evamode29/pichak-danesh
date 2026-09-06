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
    xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    streak = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-points", "id"]
        indexes = [
            models.Index(fields=["grade", "classroom"]),
            models.Index(fields=["points"]),
            models.Index(fields=["xp"]),
        ]

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    @staticmethod
    def xp_for_level(level):
        """Total XP required to reach a level using increasing level costs."""
        level = max(1, int(level))
        return 100 * (level - 1) * level // 2

    @classmethod
    def level_for_xp(cls, xp):
        """Return the highest level unlocked by the supplied XP."""
        xp = max(0, int(xp))
        level = 1
        while cls.xp_for_level(level + 1) <= xp:
            level += 1
        return level

    def refresh_level(self):
        """Recalculate the student's level from their current XP."""
        self.level = self.level_for_xp(self.xp)
        return self.level

    @property
    def level_start_xp(self):
        return self.xp_for_level(self.level)

    @property
    def next_level_xp(self):
        return self.xp_for_level(self.level + 1)

    @property
    def level_progress_percent(self):
        start = self.level_start_xp
        target = self.next_level_xp
        if target <= start:
            return 100
        return min(100, round(((self.xp - start) / (target - start)) * 100))

    @property
    def xp_to_next_level(self):
        return max(0, self.next_level_xp - self.xp)


class ParentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="parent_profile")
    mobile = models.CharField(max_length=15, unique=True)
    students = models.ManyToManyField(StudentProfile, related_name="parents", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username
