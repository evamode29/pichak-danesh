from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from openpyxl import Workbook

from core.models import UserProfile
from exams.models import (
    BankQuestion, PlacementAnswer, PlacementAttempt, PlacementDiagnosticResult,
    PlacementTest, QuestionCategory, TestBankQuestion,
)
from students.models import StudentProfile


User = get_user_model()


class QuestionBankFlowTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="bank_teacher", password="test-password-123"
        )
        UserProfile.objects.create(user=self.teacher, role=UserProfile.Role.TEACHER)

        self.student_user = User.objects.create_user(
            username="bank_student", password="test-password-123"
        )
        UserProfile.objects.create(user=self.student_user, role=UserProfile.Role.STUDENT)
        self.student = StudentProfile.objects.create(user=self.student_user, grade=6)

        self.test = PlacementTest.objects.create(
            title="آزمون بانک سؤال", grade=6, duration_minutes=10, is_active=True
        )
        self.chapter = QuestionCategory.objects.create(
            name="فصل اول", subject="math", grade=6
        )
        self.topic = QuestionCategory.objects.create(
            name="عددنویسی", subject="math", grade=6, parent=self.chapter
        )
        self.question = BankQuestion.objects.create(
            subject="math", grade=6, text="عدد بعد از ۹ چیست؟",
            option_a="۸", option_b="۱۰", option_c="۱۱", option_d="۱۲",
            correct_option="B", difficulty=1,
        )
        self.question.categories.add(self.chapter, self.topic)
        TestBankQuestion.objects.create(
            test=self.test, question=self.question, order=1
        )

    def test_teacher_can_open_question_bank(self):
        self.client.force_login(self.teacher)
        response = self.client.get(reverse("teacher-question-bank"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "بانک سؤال پیچک دانش")

    def test_excel_import_requires_preview_then_saves_rows(self):
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "سوال‌ها"
        sheet.append([
            "subject", "grade", "chapter", "topic", "subtopic", "text",
            "option_a", "option_b", "option_c", "option_d", "correct",
            "difficulty", "explanation",
        ])
        sheet.append([
            "math", 6, "فصل دوم", "کسرها", "جمع کسرها",
            "حاصل ۱/۲ + ۱/۲ چیست؟", "صفر", "یک", "دو", "سه",
            "B", 2, "دو نیم برابر یک است.",
        ])
        buffer = BytesIO()
        workbook.save(buffer)
        upload = SimpleUploadedFile(
            "question-bank.xlsx", buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        self.client.force_login(self.teacher)
        response = self.client.post(
            reverse("teacher-question-bank"),
            {"action": "preview_excel", "workbook": upload},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "پیش‌نمایش 1 سؤال آماده شد")
        self.assertEqual(BankQuestion.objects.count(), 1)

        response = self.client.post(
            reverse("teacher-question-bank"), {"action": "confirm_import"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(BankQuestion.objects.count(), 2)
        imported = BankQuestion.objects.get(text="حاصل ۱/۲ + ۱/۲ چیست؟")
        self.assertEqual(imported.correct_option, "B")
        self.assertEqual(imported.categories.count(), 3)

    def test_student_can_take_bank_test_and_answers_are_saved_per_question(self):
        self.client.force_login(self.student_user)
        response = self.client.get(reverse("student-test-list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "آزمون بانک سؤال")

        response = self.client.post(
            reverse("student-take-test", args=[self.test.pk]),
            {f"question_bank-{self.question.pk}": "B"},
        )
        self.assertEqual(response.status_code, 200)
        attempt = PlacementAttempt.objects.get(student=self.student, test=self.test)
        answer = PlacementAnswer.objects.get(attempt=attempt)
        self.assertEqual(answer.bank_question, self.question)
        self.assertEqual(answer.selected_option, "B")
        self.assertEqual(answer.correct_option, "B")
        self.assertTrue(answer.is_correct)
        self.assertEqual(answer.category_names, ["فصل اول", "عددنویسی"])
        diagnostic = PlacementDiagnosticResult.objects.get(attempt=attempt)
        self.assertEqual(diagnostic.subject, "math")
        self.assertEqual(diagnostic.correct_answers, 1)
        self.assertEqual(diagnostic.total_questions, 1)
        self.assertEqual(diagnostic.percentage, 100)
