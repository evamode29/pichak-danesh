from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import UserProfile
from students.models import StudentProfile

from .adaptive import recommended_subject
from .models import PracticeAttempt, PracticeQuestion


User = get_user_model()


class PracticeFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="practice1", password="pass12345", first_name="علی"
        )
        UserProfile.objects.create(
            user=self.user,
            role=UserProfile.Role.STUDENT,
            mobile="09120000002",
            display_name="علی",
        )
        self.student = StudentProfile.objects.create(
            user=self.user, mobile="09120000002", grade=6, level=3, points=100
        )
        self.questions = []
        for index in range(5):
            self.questions.append(
                PracticeQuestion.objects.create(
                    subject=PracticeQuestion.Subject.MATH,
                    text=f"سؤال تمرین {index + 1}",
                    option_a="گزینه الف",
                    option_b="گزینه ب",
                    option_c="گزینه ج",
                    option_d="گزینه د",
                    correct_option="A",
                    level=3,
                    difficulty=3,
                    points=10,
                )
            )
        self.client.force_login(self.user)

    def test_practice_start_uses_student_level(self):
        response = self.client.get(reverse("practice-start"))
        self.assertRedirects(response, reverse("practice-question"))
        self.assertEqual(
            self.client.session["practice_question_ids"], [q.id for q in self.questions]
        )

    def test_complete_practice_awards_points_and_records_attempts(self):
        self.client.get(reverse("practice-start"))
        for index in range(5):
            response = self.client.post(
                reverse("practice-question") + f"?q={index}",
                {"answer": "A"},
            )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("practice-result"))

        result = self.client.get(reverse("practice-result"))
        self.assertEqual(result.status_code, 200)
        self.assertContains(result, "100٪")
        self.assertEqual(PracticeAttempt.objects.filter(student=self.student).count(), 5)
        self.student.refresh_from_db()
        self.assertEqual(self.student.points, 150)

    def test_practice_result_requires_active_session(self):
        response = self.client.get(reverse("practice-result"))
        self.assertRedirects(
            response,
            reverse("practice-start"),
            target_status_code=302,
        )


    def test_adaptive_practice_focuses_on_recent_weak_subject(self):
        science_questions = []
        for index in range(2):
            science_questions.append(
                PracticeQuestion.objects.create(
                    subject=PracticeQuestion.Subject.SCIENCE,
                    text=f"سؤال علوم {index + 1}",
                    option_a="گزینه الف",
                    option_b="گزینه ب",
                    option_c="گزینه ج",
                    option_d="گزینه د",
                    correct_option="A",
                    level=3,
                    difficulty=2,
                    points=10,
                )
            )
            PracticeAttempt.objects.create(
                student=self.student,
                question=science_questions[-1],
                selected_option="B",
                is_correct=False,
                points_earned=0,
            )

        self.assertEqual(recommended_subject(self.student), "science")
        response = self.client.get(reverse("practice-start"))
        self.assertRedirects(response, reverse("practice-question"))
        question_ids = self.client.session["practice_question_ids"]
        self.assertEqual(question_ids[:2], [q.id for q in science_questions])
        self.assertEqual(self.client.session["practice_weak_subject"], "science")

    def test_practice_allows_review_when_no_unseen_questions_remain(self):
        for question in self.questions:
            PracticeAttempt.objects.create(
                student=self.student,
                question=question,
                selected_option="A",
                is_correct=True,
                points_earned=question.points,
            )

        response = self.client.get(reverse("practice-start"))
        self.assertRedirects(response, reverse("practice-question"))
        self.assertEqual(
            len(self.client.session["practice_question_ids"]),
            5,
        )
