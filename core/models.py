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

    def __str__(self): return self.display_name or self.user.get_full_name() or self.user.username


class ClassRoom(models.Model):
    name = models.CharField(max_length=120)
    grade = models.PositiveSmallIntegerField(default=6)
    academic_year = models.CharField(max_length=20, blank=True)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="teaching_classes")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["grade", "name"]
        indexes = [models.Index(fields=["grade", "is_active"]), models.Index(fields=["teacher", "is_active"])]

    def __str__(self): return self.name


class DailyTask(models.Model):
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name="daily_tasks")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    task_date = models.DateField()
    max_score = models.PositiveSmallIntegerField(default=20)
    due_time = models.TimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_daily_tasks")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-task_date", "-id"]
        indexes = [models.Index(fields=["classroom", "task_date"])]

    def __str__(self): return f"{self.classroom} - {self.title} - {self.task_date}"


class StudentTask(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "انجام نشده"
        DONE = "done", "انجام شد"
        REVIEW = "review", "نیاز به بررسی"

    task = models.ForeignKey(DailyTask, on_delete=models.CASCADE, related_name="student_tasks")
    student = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="task_records")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    score = models.PositiveSmallIntegerField(null=True, blank=True)
    note = models.CharField(max_length=500, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["task", "student"], name="unique_daily_task_student")]
        ordering = ["student__user__first_name", "student__user__last_name"]

    def __str__(self): return f"{self.student} - {self.task}"
