from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import ClassRoom, UserProfile
from .models import ParentProfile, StudentProfile


User = get_user_model()


class StudentProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="student1", password="secret123")
        self.classroom = ClassRoom.objects.create(name="کلاس ششم الف", grade=6)

    def test_student_profile_defaults_and_classroom(self):
        student = StudentProfile.objects.create(
            user=self.user,
            mobile="09120000000",
            classroom=self.classroom,
        )
        self.assertEqual(student.grade, 6)
        self.assertTrue(student.is_free)
        self.assertEqual(student.points, 0)
        self.assertEqual(student.classroom, self.classroom)

    def test_parent_can_be_linked_to_student(self):
        student = StudentProfile.objects.create(user=self.user, mobile="09120000001")
        parent_user = User.objects.create_user(username="parent1", password="secret123")
        parent = ParentProfile.objects.create(user=parent_user, mobile="09120000002")
        parent.students.add(student)
        self.assertIn(parent, student.parents.all())


class StudentApiTests(TestCase):
    def test_students_endpoint_returns_results(self):
        user = User.objects.create_user(username="student2", password="secret123")
        UserProfile.objects.create(user=user, role=UserProfile.Role.STUDENT)
        StudentProfile.objects.create(user=user, mobile="09120000003")
        self.client.force_login(user)
        response = self.client.get(reverse("api-students"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["results"]), 1)


class StudentXPLevelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="xp_student",
            password="secret123",
        )
        self.student = StudentProfile.objects.create(
            user=self.user,
            mobile="09120000010",
        )

    def test_xp_level_boundaries(self):
        cases = [
            (0, 1),
            (99, 1),
            (100, 2),
            (299, 2),
            (300, 3),
            (599, 3),
            (600, 4),
            (1000, 5),
        ]

        for xp, expected_level in cases:
            with self.subTest(xp=xp):
                self.student.xp = xp
                self.student.refresh_level()
                self.assertEqual(self.student.level, expected_level)

    def test_xp_progress_properties(self):
        self.student.xp = 150
        self.student.refresh_level()

        self.assertEqual(self.student.level, 2)
        self.assertEqual(self.student.level_start_xp, 100)
        self.assertEqual(self.student.next_level_xp, 300)
        self.assertEqual(self.student.xp_to_next_level, 150)
        self.assertEqual(self.student.level_progress_percent, 25)

    def test_level_up_from_xp(self):
        self.student.xp = 99
        self.student.refresh_level()
        self.assertEqual(self.student.level, 1)

        self.student.xp += 1
        self.student.refresh_level()

        self.assertEqual(self.student.xp, 100)
        self.assertEqual(self.student.level, 2)
