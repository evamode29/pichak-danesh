from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import ClassRoom, UserProfile
from exams.models import BankQuestion, PlacementAnswer, PlacementAttempt, PlacementTest
from students.models import StudentProfile


User = get_user_model()


class TeacherLearningReportTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username="report_teacher", password="test-password-123")
        UserProfile.objects.create(user=self.teacher, role=UserProfile.Role.TEACHER)
        self.classroom = ClassRoom.objects.create(name="ششم ۱", grade=6, teacher=self.teacher)
        self.student_user = User.objects.create_user(username="report_student", password="test-password-123")
        UserProfile.objects.create(user=self.student_user, role=UserProfile.Role.STUDENT)
        self.student = StudentProfile.objects.create(user=self.student_user, grade=6, classroom=self.classroom)
        self.test = PlacementTest.objects.create(title="آزمون گزارش", grade=6)
        self.attempt = PlacementAttempt.objects.create(
            student=self.student, test=self.test, score=50,
            correct_answers=1, total_questions=2,
        )
        question = BankQuestion.objects.create(
            subject="math", grade=6, text="سؤال گزارش", option_a="الف",
            option_b="ب", option_c="ج", option_d="د", correct_option="A",
        )
        PlacementAnswer.objects.create(
            attempt=self.attempt, bank_question=question, question_text=question.text,
            selected_option="A", correct_option="A", is_correct=True,
            subject="math", category_names=["عددها", "کسرها", "جمع کسرها"],
        )
        PlacementAnswer.objects.create(
            attempt=self.attempt, bank_question=question, question_text=question.text,
            selected_option="B", correct_option="A", is_correct=False,
            subject="math", category_names=["عددها", "کسرها", "جمع کسرها"],
        )

    def test_teacher_report_summarizes_subject_and_curriculum_levels(self):
        self.client.force_login(self.teacher)
        response = self.client.get(reverse("teacher-learning-reports"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "گزارش مسیر یادگیری")
        self.assertContains(response, "ریاضی")
        self.assertContains(response, "جمع کسرها")
        self.assertEqual(response.context["overall_percentage"], 50)
        self.assertEqual(response.context["answer_count"], 2)
        self.assertEqual(len(response.context["category_rows"]), 3)

    def test_report_keeps_multiple_category_branches_separate(self):
        answer = self.attempt.answers.first()
        answer.category_names = ["عددها", "کسرها", "جمع کسرها"]
        answer.category_paths = [
            ["عددها", "کسرها", "جمع کسرها"],
            ["عددها", "اعشار", "مقایسه اعشار"],
        ]
        answer.save(update_fields=["category_names", "category_paths"])

        self.client.force_login(self.teacher)
        response = self.client.get(reverse("teacher-learning-reports"))

        self.assertEqual(response.status_code, 200)
        paths = {row["path"] for row in response.context["category_rows"]}
        self.assertIn("عددها ← کسرها ← جمع کسرها", paths)
        self.assertIn("عددها ← اعشار ← مقایسه اعشار", paths)
        self.assertNotIn("عددها ← کسرها ← مقایسه اعشار", paths)

    def test_teacher_cannot_view_student_outside_scope(self):
        other_user = User.objects.create_user(username="outside_student", password="test-password-123")
        UserProfile.objects.create(user=other_user, role=UserProfile.Role.STUDENT)
        outside = StudentProfile.objects.create(user=other_user, grade=6)
        self.client.force_login(self.teacher)
        response = self.client.get(
            reverse("teacher-learning-reports"), {"student": outside.pk}
        )
        self.assertEqual(response.status_code, 404)

    def test_teacher_without_classroom_sees_no_student_data(self):
        unassigned_teacher = User.objects.create_user(
            username="teacher_without_class", password="test-password-123"
        )
        UserProfile.objects.create(
            user=unassigned_teacher, role=UserProfile.Role.TEACHER
        )
        self.client.force_login(unassigned_teacher)

        response = self.client.get(reverse("teacher-learning-reports"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["student_count"], 0)
        self.assertEqual(response.context["attempt_count"], 0)
        self.assertEqual(response.context["answer_count"], 0)
        self.assertEqual(response.context["performance_rows"], [])

    def test_student_cannot_open_teacher_reports(self):
        self.client.force_login(self.student_user)
        response = self.client.get(reverse("teacher-learning-reports"))
        self.assertEqual(response.status_code, 302)
