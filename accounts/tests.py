from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .models import Task


class TaskDetailViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="task-owner", password="password")
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_patch_nonexistent_task_returns_not_found(self):
        response = self.client.patch(
            reverse("api_task_detail", kwargs={"pk": 999999}),
            {"completed": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error": "Task not found."})



class TaskCollectionViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="task-collection-owner", password="password")
        self.other_user = User.objects.create_user(username="other-task-owner", password="password")
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_list_tasks_returns_active_tasks_in_display_order(self):
        pending_low = Task.objects.create(user=self.user, title="Pending low", priority="Low")
        pending_high = Task.objects.create(user=self.user, title="Pending high", priority="High")
        completed_high = Task.objects.create(
            user=self.user, title="Completed high", priority="High", completed=True
        )
        Task.objects.create(user=self.user, title="Deleted task", is_deleted=True)
        Task.objects.create(user=self.other_user, title="Another user's task", priority="High")

        response = self.client.get(reverse("api_tasks"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [task["id"] for task in response.data],
            [pending_high.id, pending_low.id, completed_high.id],
        )

    def test_create_task_creates_task_for_authenticated_user(self):
        response = self.client.post(
            reverse("api_tasks"),
            {"title": "New task", "priority": "Medium"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "New task")
        self.assertEqual(response.data["priority"], "Medium")
        self.assertTrue(
            Task.objects.filter(
                id=response.data["id"], user=self.user, title="New task", priority="Medium"
            ).exists()
        )


class RegistrationViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_creates_user_and_returns_token(self):
        response = self.client.post(
            reverse("api_register"),
            {"username": "new-user", "password": "password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"]["username"], "new-user")
        self.assertTrue(response.data["token"])
        self.assertTrue(User.objects.filter(username="new-user").exists())

    def test_registering_duplicate_username_returns_bad_request(self):
        registration_data = {"username": "duplicate-user", "password": "password"}
        first_response = self.client.post(
            reverse("api_register"), registration_data, format="json"
        )
        second_response = self.client.post(
            reverse("api_register"), registration_data, format="json"
        )

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(second_response.data, {"error": "Username already exists."})


class DashboardViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="dashboard-user", password="password")
        self.other_user = User.objects.create_user(username="other-user", password="password")
        self.pending_task = Task.objects.create(user=self.user, title="Pending task")
        self.completed_task = Task.objects.create(
            user=self.user, title="Completed task", completed=True
        )
        Task.objects.create(user=self.user, title="Deleted task", is_deleted=True)
        Task.objects.create(user=self.other_user, title="Another user's task")
        self.client.force_login(self.user)

    def test_dashboard_displays_only_active_tasks_for_current_user(self):
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, "dashboard.html")
        self.assertEqual(
            list(response.context["tasks"]),
            [self.pending_task, self.completed_task],
        )
        self.assertEqual(response.context["total_pending"], 1)
        self.assertEqual(response.context["total_completed"], 1)
