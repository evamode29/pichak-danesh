from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import ClassRoom
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
        StudentProfile.objects.create(user=user, mobile="09120000003")
        response = self.client.get(reverse("api-students"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["results"]), 1)
