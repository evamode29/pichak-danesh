from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import UserProfile
from exams.models import PlacementAttempt
from students.models import StudentProfile


User = get_user_model()


class SimpleVisualIQTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="visual_iq_student",
            password="test-password-123",
            first_name="دانش‌آموز",
        )
        UserProfile.objects.create(user=self.user, role=UserProfile.Role.STUDENT)
        self.student = StudentProfile.objects.create(user=self.user, grade=6)
        self.client.force_login(self.user)

    def test_visual_iq_rejects_invalid_option_values(self):
        response = self.client.post(
            reverse("simple-iq"),
            {"q1": "X", "q2": "C", "q3": "B", "q4": "B", "q5": "C"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "گزینه معتبر")
        self.assertFalse(
            PlacementAttempt.objects.filter(student=self.student).exists()
        )

    def test_visual_iq_records_a_valid_submission(self):
        response = self.client.post(
            reverse("simple-iq"),
            {"q1": "A", "q2": "C", "q3": "B", "q4": "B", "q5": "C"},
        )

        self.assertEqual(response.status_code, 200)
        attempt = PlacementAttempt.objects.get(student=self.student)
        self.assertEqual(attempt.correct_answers, 5)
        self.assertEqual(attempt.total_questions, 5)
        self.assertEqual(attempt.score, 100)
