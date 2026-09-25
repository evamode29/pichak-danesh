import json
from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import ClassRoom, DailyTask, StudentTask, UserProfile
from students.models import StudentProfile


User = get_user_model()


class CoreModelTests(TestCase):
    def test_user_profile_role_and_classroom(self):
        user = User.objects.create_user(username="teacher1", password="secret123", first_name="علی")
        profile = UserProfile.objects.create(user=user, role=UserProfile.Role.TEACHER)
        classroom = ClassRoom.objects.create(name="ششم الف", grade=6, teacher=user)
        self.assertEqual(profile.role, UserProfile.Role.TEACHER)
        self.assertEqual(classroom.teacher, user)
        self.assertEqual(str(classroom), "ششم الف")


class CoreApiTests(TestCase):
    def test_classrooms_endpoint(self):
        user = User.objects.create_user(username="teacher2", password="secret123", first_name="رضا")
        UserProfile.objects.create(user=user, role=UserProfile.Role.TEACHER)
        ClassRoom.objects.create(name="ششم ب", grade=6, teacher=user)
        self.client.force_login(user)
        response = self.client.get(reverse("api-classrooms"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"][0]["teacher_name"], "رضا")

    def test_login_and_me(self):
        user = User.objects.create_user(username="loginuser", password="secret123")
        UserProfile.objects.create(user=user, role=UserProfile.Role.STUDENT, mobile="09120000004")
        response = self.client.post(
            reverse("api-auth-login"),
            data=json.dumps({"username": "loginuser", "password": "secret123"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user"]["role"], "student")

        me = self.client.get(reverse("api-auth-me"))
        self.assertEqual(me.status_code, 200)
        self.assertTrue(me.json()["authenticated"])

    def test_login_rejects_invalid_credentials(self):
        response = self.client.post(
            reverse("api-auth-login"),
            data=json.dumps({"username": "missing", "password": "wrong"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)


class HomeworkFlowTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username="teacher_hw", password="secret123")
        UserProfile.objects.create(user=self.teacher, role=UserProfile.Role.TEACHER)
        self.classroom = ClassRoom.objects.create(name="ششم تکلیف", grade=6, teacher=self.teacher)
        self.student_user = User.objects.create_user(
            username="student_hw", password="secret123", first_name="دانش‌آموز"
        )
        UserProfile.objects.create(
            user=self.student_user,
            role=UserProfile.Role.STUDENT,
            mobile="09120000009",
        )
        self.student = StudentProfile.objects.create(
            user=self.student_user,
            classroom=self.classroom,
            grade=6,
            mobile="09120000009",
        )
        self.task = DailyTask.objects.create(
            classroom=self.classroom,
            title="تمرین امروز",
            task_date=date.today(),
            created_by=self.teacher,
        )
        StudentTask.objects.create(task=self.task, student=self.student)

    def test_student_can_mark_today_homework_done(self):
        self.client.force_login(self.student_user)
        response = self.client.post(
            reverse("student-homework"),
            {"action": "mark_done", "task_id": self.task.id},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            StudentTask.objects.get(task=self.task, student=self.student).status,
            StudentTask.Status.DONE,
        )

    def test_student_cannot_mark_another_class_task_done(self):
        other_class = ClassRoom.objects.create(name="ششم دیگر", grade=6, teacher=self.teacher)
        other_task = DailyTask.objects.create(
            classroom=other_class,
            title="تکلیف دیگر",
            task_date=date.today(),
            created_by=self.teacher,
        )
        self.client.force_login(self.student_user)
        response = self.client.post(
            reverse("student-homework"),
            {"action": "mark_done", "task_id": other_task.id},
        )
        self.assertEqual(response.status_code, 404)
class TeacherHomeworkReportTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username="teacher_report", password="secret123")
        UserProfile.objects.create(user=self.teacher, role=UserProfile.Role.TEACHER)
        self.classroom = ClassRoom.objects.create(name="ششم گزارش", grade=6, teacher=self.teacher)
        self.student_user = User.objects.create_user(
            username="student_report", password="secret123", first_name="گزارش"
        )
        UserProfile.objects.create(
            user=self.student_user, role=UserProfile.Role.STUDENT, mobile="09120000010"
        )
        self.student = StudentProfile.objects.create(
            user=self.student_user,
            classroom=self.classroom,
            grade=6,
            mobile="09120000010",
        )
        self.task = DailyTask.objects.create(
            classroom=self.classroom,
            title="گزارش تکلیف",
            task_date=date.today(),
            created_by=self.teacher,
        )
        self.record = StudentTask.objects.create(
            task=self.task, student=self.student, status=StudentTask.Status.DONE, score=18
        )

    def test_teacher_student_detail_contains_homework_report(self):
        self.client.force_login(self.teacher)
        response = self.client.get(
            reverse("teacher-student-detail", args=[self.student.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["homework_done"], 1)
        self.assertEqual(response.context["homework_total"], 1)
        self.assertContains(response, "گزارش تکلیف")

    def test_teacher_class_detail_contains_today_homework_summary(self):
        self.client.force_login(self.teacher)
        response = self.client.get(
            reverse("teacher-class-detail", args=[self.classroom.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["homework_done"], 1)
        self.assertEqual(response.context["homework_total"], 1)

