from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Task, Team


class TaskTeamAuthorizationTests(TestCase):

    def test_cannot_assign_foreign_team(self):
        alice = User.objects.create_user(username="alice")
        bob = User.objects.create_user(username="bob")

        foreign_team = Team.objects.create(name="Bob Team")
        foreign_team.users.add(bob)

        self.client.force_login(alice)

        response = self.client.post(
            reverse("task:create_task"),
            {
                "title": "Unauthorized task",
                "private": "on",
                "status": "todo",
                "teams": [foreign_team.pk],
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("teams", response.context["form"].errors)
        self.assertFalse(
            Task.objects.filter(title="Unauthorized task").exists()
        )

    def test_cannot_add_foreign_team_on_update(self):
        alice = User.objects.create_user(username="alice")
        bob = User.objects.create_user(username="bob")

        task = Task.objects.create(
            title="Original title",
            creator=alice
        )

        foreign_team = Team.objects.create(name="Bob Team")
        foreign_team.users.add(bob)

        self.client.force_login(alice)

        response = self.client.post(
            reverse("task:update_task", args=[task.pk]),
            {
                "title": "Modified title",
                "status": "todo",
                "teams": [foreign_team.pk],
            }
        )

        task.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertIn("teams", response.context["form"].errors)
        self.assertEqual(task.title, "Original title")
        self.assertFalse(task.teams.filter(pk=foreign_team.pk).exists())


    def test_existing_team_relationship_is_preserved(self):
        alice = User.objects.create_user(username="alice")
        bob = User.objects.create_user(username="bob")

        team = Team.objects.create(name="Existing Team")
        team.users.add(bob)

        task = Task.objects.create(
            title="Original title",
            creator=alice
        )
        task.teams.add(team)

        self.client.force_login(alice)

        response = self.client.post(
            reverse("task:update_task", args=[task.pk]),
            {
                "title": "Updated title",
                "status": "todo",
                "teams": [team.pk],
            }
        )

        task.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(task.title, "Updated title")
        self.assertTrue(task.teams.filter(pk=team.pk).exists())