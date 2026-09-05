from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class UserProfile(models.Model):
    class Role(models.TextChoices):
        STUDENT = "student", "دانش‌آموز"
        TEACHER = "teacher", "معلم"
        PARENT = "parent", "والد"
        ADMIN = "admin", "مدیر"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    mobile = models.CharField(max_length=15, unique=True, null=True, blank=True)
    display_name = models.CharField(max_length=120, blank=True)
    is_active_profile = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.display_name or self.user.get_full_name() or self.user.username


class ClassRoom(models.Model):
    name = models.CharField(max_length=120)
    grade = models.PositiveSmallIntegerField(default=6)
    academic_year = models.CharField(max_length=20, blank=True)
    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teaching_classes",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["grade", "name"]
        indexes = [
            models.Index(fields=["grade", "is_active"]),
            models.Index(fields=["teacher", "is_active"]),
        ]

    def __str__(self):
        return self.name
