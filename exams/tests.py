from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import UserProfile
from .models import PlacementAttempt, PlacementQuestion, PlacementTest
from students.models import StudentProfile

User = get_user_model()


class PlacementFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="student1", password="pass12345", first_name="علی")
        UserProfile.objects.create(
            user=self.user,
            role=UserProfile.Role.STUDENT,
            mobile="09120000001",
            display_name="علی",
        )
        self.student = StudentProfile.objects.create(
            user=self.user,
            mobile="09120000001",
            grade=6,
        )
        self.test = PlacementTest.objects.create(
            title="تعیین سطح آزمایشی",
            grade=6,
            duration_minutes=15,
            is_active=True,
        )
        PlacementQuestion.objects.create(
            test=self.test,
            text="۲ + ۲ چند می‌شود؟",
            option_a="۳",
            option_b="۴",
            option_c="۵",
            option_d="۶",
            correct_option="B",
            subject=PlacementQuestion.Subject.MATH,
            difficulty=1,
            order=1,
        )
        PlacementQuestion.objects.create(
            test=self.test,
            text="پایتخت ایران کدام است؟",
            option_a="تهران",
            option_b="مشهد",
            option_c="شیراز",
            option_d="تبریز",
            correct_option="A",
            subject=PlacementQuestion.Subject.SOCIAL,
            difficulty=1,
            order=2,
        )
        self.client.force_login(self.user)

    def test_start_redirects_to_first_question(self):
        response = self.client.get(reverse("placement-start"))
        self.assertRedirects(response, reverse("placement-question"))
        self.assertEqual(self.client.session["placement_test_id"], self.test.id)

    def test_question_page_shows_options(self):
        self.client.get(reverse("placement-start"))
        response = self.client.get(reverse("placement-question"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "۲ + ۲ چند می‌شود؟")
        self.assertContains(response, "۴")

    def test_complete_placement_creates_attempt_and_updates_student(self):
        self.client.get(reverse("placement-start"))
        self.client.post(reverse("placement-question") + "?q=0", {"answer": "B"})
        response = self.client.post(reverse("placement-question") + "?q=1", {"answer": "A"})

        self.assertRedirects(response, reverse("placement-result"))
        response = self.client.get(reverse("placement-result"))

        self.assertEqual(response.status_code, 200)
        attempt = PlacementAttempt.objects.get(student=self.student, test=self.test)
        self.assertEqual(attempt.score, 100)
        self.assertEqual(attempt.correct_answers, 2)
        self.assertEqual(attempt.total_questions, 2)
        self.assertEqual(attempt.level, 10)
        self.student.refresh_from_db()
        self.assertEqual(self.student.level, 10)
        self.assertEqual(self.student.points, 1000)
