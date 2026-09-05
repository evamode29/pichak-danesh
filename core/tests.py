import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import ClassRoom, UserProfile


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
        ClassRoom.objects.create(name="ششم ب", grade=6, teacher=user)
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
