from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class UserProfile(models.Model):
    class Role(models.TextChoices):
        STUDENT = "student", "دانش‌آموز"
        TEACHER = "teacher", "معلم"
        PARENT = "parent", "والد"
        ADMIN = "admin", "مدیر اصلی"
        CONTENT_MANAGER = "content_manager", "مدیر محتوا"

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


class TeacherStudentNote(models.Model):
    """Teacher-entered educational notes and AI feedback for one student."""
    class Kind(models.TextChoices):
        NOTE = "note", "یادداشت معلم"
        FEEDBACK = "feedback", "بازخورد"
        AI_ANALYSIS = "ai_analysis", "تحلیل هوش مصنوعی"

    student = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="teacher_notes")
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="student_notes")
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.NOTE)
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [models.Index(fields=["student", "kind", "-created_at"])]

    def __str__(self):
        return f"{self.student} - {self.get_kind_display()}"


class StudentEducationalAssessment(models.Model):
    """Periodic teacher assessment of learning and study skills."""
    student = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="educational_assessments")
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="educational_assessments")
    assessment_date = models.DateField()
    participation = models.PositiveSmallIntegerField(default=3)
    effort = models.PositiveSmallIntegerField(default=3)
    focus = models.PositiveSmallIntegerField(default=3)
    independence = models.PositiveSmallIntegerField(default=3)
    time_management = models.PositiveSmallIntegerField(default=3)
    responsibility = models.PositiveSmallIntegerField(default=3)
    cooperation = models.PositiveSmallIntegerField(default=3)
    problem_solving = models.PositiveSmallIntegerField(default=3)
    accuracy = models.PositiveSmallIntegerField(default=3)
    perseverance = models.PositiveSmallIntegerField(default=3)
    strengths = models.TextField(blank=True)
    needs_improvement = models.TextField(blank=True)
    teacher_summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-assessment_date", "-id"]
        indexes = [models.Index(fields=["student", "-assessment_date"])]

    def __str__(self):
        return f"{self.student} - ارزیابی {self.assessment_date}"

    @property
    def overall_score(self):
        fields = [
            self.participation, self.effort, self.focus, self.independence,
            self.time_management, self.responsibility, self.cooperation,
            self.problem_solving, self.accuracy, self.perseverance,
        ]
        return round(sum(fields) / len(fields), 1)


class StudentGoal(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "در حال پیگیری"
        DONE = "done", "انجام شد"
        PAUSED = "paused", "متوقف"

    student = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="learning_goals")
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="student_goals")
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=50, blank=True)
    target_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["status", "target_date", "-id"]
        indexes = [models.Index(fields=["student", "status"])]

    def __str__(self):
        return self.title
