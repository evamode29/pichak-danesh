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


class StudentAttendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = "present", "حاضر"
        ABSENT = "absent", "غایب"
        LATE = "late", "با تأخیر"

    class Mood(models.TextChoices):
        GREAT = "great", "خیلی خوب"
        GOOD = "good", "خوب"
        NORMAL = "normal", "عادی"
        LOW = "low", "کم‌انرژی"

    student = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="attendance_records")
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="student_attendance_records")
    date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PRESENT)
    mood = models.CharField(max_length=20, choices=Mood.choices, blank=True)
    note = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]
        constraints = [models.UniqueConstraint(fields=["student", "date"], name="unique_student_attendance_date")]
        indexes = [models.Index(fields=["student", "-date"])]

    def __str__(self):
        return f"{self.student} - {self.date}"


class StudentFamilyContact(models.Model):
    class Kind(models.TextChoices):
        CALL = "call", "تماس"
        MEETING = "meeting", "جلسه"
        MESSAGE = "message", "پیام"
        FOLLOWUP = "followup", "پیگیری"

    student = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="family_contacts")
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="student_family_contacts")
    contact_date = models.DateField()
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.CALL)
    summary = models.TextField()
    follow_up = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-contact_date", "-id"]
        indexes = [models.Index(fields=["student", "-contact_date"])]

    def __str__(self):
        return f"{self.student} - {self.get_kind_display()} - {self.contact_date}"


class StudentStudySession(models.Model):
    """A recorded study session for annual learning history."""
    student = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="study_sessions")
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="student_study_sessions")
    session_date = models.DateField()
    subject = models.CharField(max_length=50, blank=True)
    topic = models.CharField(max_length=150, blank=True)
    minutes = models.PositiveIntegerField(default=0)
    questions_count = models.PositiveIntegerField(default=0)
    correct_count = models.PositiveIntegerField(default=0)
    completion = models.PositiveSmallIntegerField(default=100)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-session_date", "-id"]
        indexes = [models.Index(fields=["student", "-session_date"])]

    def __str__(self):
        return f"{self.student} - {self.session_date} - {self.subject}"


class StudentBehaviorObservation(models.Model):
    """Objective classroom observations; not a medical or psychological diagnosis."""
    class Type(models.TextChoices):
        POSITIVE = "positive", "نقطه قوت"
        CHALLENGE = "challenge", "نیازمند پیگیری"

    student = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="behavior_observations")
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="student_behavior_observations")
    observation_date = models.DateField()
    observation_type = models.CharField(max_length=20, choices=Type.choices, default=Type.POSITIVE)
    area = models.CharField(max_length=80, blank=True)
    observation = models.TextField()
    action_taken = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-observation_date", "-id"]
        indexes = [models.Index(fields=["student", "-observation_date"])]

    def __str__(self):
        return f"{self.student} - {self.observation_date}"


class StudentPortfolioItem(models.Model):
    student = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="portfolio_items")
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="student_portfolio_items")
    title = models.CharField(max_length=200)
    item_date = models.DateField()
    subject = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="student_portfolio/%Y/%m/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-item_date", "-id"]
        indexes = [models.Index(fields=["student", "-item_date"])]

    def __str__(self):
        return self.title


class StudentAnnualReview(models.Model):
    class Period(models.TextChoices):
        START = "start", "ابتدای سال"
        MID = "mid", "میان‌سال"
        END = "end", "پایان سال"

    student = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE, related_name="annual_reviews")
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="student_annual_reviews")
    academic_year = models.CharField(max_length=20)
    period = models.CharField(max_length=10, choices=Period.choices)
    review_date = models.DateField()
    academic_summary = models.TextField(blank=True)
    strengths = models.TextField(blank=True)
    needs_improvement = models.TextField(blank=True)
    next_steps = models.TextField(blank=True)
    parent_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-review_date", "-id"]
        constraints = [
            models.UniqueConstraint(fields=["student", "academic_year", "period"], name="unique_student_annual_review_period"),
        ]
        indexes = [models.Index(fields=["student", "-review_date"])]

    def __str__(self):
        return f"{self.student} - {self.academic_year} - {self.get_period_display()}"
