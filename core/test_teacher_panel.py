from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import ClassRoom, DailyTask, StudentTask, UserProfile
from students.models import StudentProfile


User = get_user_model()


class TeacherPanelTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher_panel", password="test-password-123"
        )
        UserProfile.objects.create(
            user=self.teacher, role=UserProfile.Role.TEACHER
        )
        self.student_users = []
        self.students = []
        for index in range(2):
            user = User.objects.create_user(
                username=f"student_panel_{index}",
                password="test-password-123",
                first_name=f"دانش‌آموز {index + 1}",
            )
            UserProfile.objects.create(
                user=user, role=UserProfile.Role.STUDENT
            )
            profile = StudentProfile.objects.create(user=user, grade=6)
            self.student_users.append(user)
            self.students.append(profile)

        self.client.force_login(self.teacher)

    def test_teacher_dashboard_displays_existing_students(self):
        response = self.client.get(reverse("simple-teacher"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["student_count"], 2)
        self.assertContains(response, "دانش‌آموز 1")
        self.assertContains(response, "دانش‌آموز 2")

    def test_setup_class_assigns_students_without_recreating_accounts(self):
        user_count = User.objects.count()
        profile_count = UserProfile.objects.count()
        student_count = StudentProfile.objects.count()

        response = self.client.post(
            reverse("teacher-activities"), {"action": "setup_class"}
        )

        self.assertEqual(response.status_code, 200)
        classroom = ClassRoom.objects.get(name="ششم ۱", grade=6)
        self.assertEqual(classroom.teacher, self.teacher)
        self.assertEqual(
            StudentProfile.objects.filter(classroom=classroom).count(), 2
        )
        self.assertEqual(User.objects.count(), user_count)
        self.assertEqual(UserProfile.objects.count(), profile_count)
        self.assertEqual(StudentProfile.objects.count(), student_count)

    def test_create_activity_assigns_one_record_per_class_student(self):
        classroom = ClassRoom.objects.create(
            name="ششم ۱", grade=6, teacher=self.teacher
        )
        StudentProfile.objects.filter(pk__in=[s.pk for s in self.students]).update(
            classroom=classroom
        )

        response = self.client.post(
            reverse("teacher-activities"),
            {
                "action": "create_task",
                "classroom_id": classroom.pk,
                "title": "تمرین ریاضی",
                "description": "حل تمرین‌های کتاب",
                "task_date": date.today().isoformat(),
                "max_score": "20",
            },
        )

        self.assertEqual(response.status_code, 200)
        task = DailyTask.objects.get(title="تمرین ریاضی")
        self.assertEqual(task.student_tasks.count(), 2)
        self.assertEqual(
            task.student_tasks.values_list("student_id", flat=True).count(), 2
        )

    def test_teacher_can_record_student_feedback_and_score(self):
        classroom = ClassRoom.objects.create(
            name="ششم ۱", grade=6, teacher=self.teacher
        )
        student = self.students[0]
        student.classroom = classroom
        student.save(update_fields=["classroom"])
        task = DailyTask.objects.create(
            classroom=classroom,
            title="تمرین امروز",
            task_date=date.today(),
            max_score=20,
            created_by=self.teacher,
        )
        record = StudentTask.objects.create(task=task, student=student, status=StudentTask.Status.REVIEW)

        response = self.client.post(
            reverse("teacher-activities"),
            {
                "action": "review_task",
                "record_id": record.pk,
                "status": StudentTask.Status.DONE,
                "score": "18",
                "note": "آفرین، با دقت حل شده است.",
            },
        )

        self.assertEqual(response.status_code, 200)
        record.refresh_from_db()
        self.assertEqual(record.status, StudentTask.Status.DONE)
        self.assertEqual(record.score, 18)
        self.assertEqual(record.note, "آفرین، با دقت حل شده است.")

    def test_teacher_cannot_review_another_teachers_task(self):
        other_teacher = User.objects.create_user(
            username="other_teacher", password="test-password-123"
        )
        UserProfile.objects.create(
            user=other_teacher, role=UserProfile.Role.TEACHER
        )
        other_class = ClassRoom.objects.create(
            name="کلاس دیگر", grade=6, teacher=other_teacher
        )
        task = DailyTask.objects.create(
            classroom=other_class,
            title="فعالیت خصوصی",
            task_date=date.today(),
            created_by=other_teacher,
        )
        record = StudentTask.objects.create(task=task, student=self.students[0])

        response = self.client.post(
            reverse("teacher-activities"),
            {
                "action": "review_task",
                "record_id": record.pk,
                "status": StudentTask.Status.DONE,
                "score": "20",
            },
        )

        self.assertEqual(response.status_code, 404)
        record.refresh_from_db()
        self.assertEqual(record.status, StudentTask.Status.PENDING)

    def test_teacher_can_open_student_learning_profile(self):
        response = self.client.get(
            reverse("teacher-student-detail", args=[self.students[0].pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "دانش‌آموز 1")


class StudentLearningPanelTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="student_view_teacher", password="test-password-123"
        )
        UserProfile.objects.create(user=self.teacher, role=UserProfile.Role.TEACHER)
        self.student_user = User.objects.create_user(
            username="student_view_user",
            password="test-password-123",
            first_name="آراد",
        )
        UserProfile.objects.create(user=self.student_user, role=UserProfile.Role.STUDENT)
        self.student = StudentProfile.objects.create(user=self.student_user, grade=6)
        self.classroom = ClassRoom.objects.create(
            name="ششم ۱", grade=6, teacher=self.teacher
        )
        self.student.classroom = self.classroom
        self.student.save(update_fields=["classroom"])
        self.task = DailyTask.objects.create(
            classroom=self.classroom,
            title="تمرین ریاضی",
            description="پنج مسئله حل کن.",
            task_date=date.today(),
            max_score=20,
            created_by=self.teacher,
        )
        self.record = StudentTask.objects.create(task=self.task, student=self.student)
        self.client.force_login(self.student_user)

    def test_student_dashboard_shows_assigned_learning_tasks(self):
        response = self.client.get(reverse("simple-student"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "تمرین ریاضی")
        self.assertContains(response, "پنج مسئله حل کن.")
        self.assertContains(response, "ارسال پاسخ برای معلم")

    def test_student_can_submit_task_for_teacher_review(self):
        response = self.client.post(
            reverse("simple-student"),
            {"action": "submit_task", "record_id": self.record.pk, "answer_text": "پاسخ تمرین"},
        )
        self.assertEqual(response.status_code, 200)
        self.record.refresh_from_db()
        self.assertEqual(self.record.status, StudentTask.Status.REVIEW)
        self.assertContains(response, "با موفقیت برای بررسی معلم ارسال شد")

    def test_student_cannot_submit_another_students_task(self):
        other_user = User.objects.create_user(
            username="another_student", password="test-password-123"
        )
        UserProfile.objects.create(user=other_user, role=UserProfile.Role.STUDENT)
        other_student = StudentProfile.objects.create(user=other_user, grade=6)
        self.client.force_login(other_user)
        response = self.client.post(
            reverse("simple-student"),
            {"action": "submit_task", "record_id": self.record.pk},
        )
        self.assertEqual(response.status_code, 404)
        self.record.refresh_from_db()
        self.assertEqual(self.record.status, StudentTask.Status.PENDING)
