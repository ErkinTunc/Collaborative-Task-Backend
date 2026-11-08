from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Task, Team

# ----------------- Task Team Authorization Tets ---------------------------

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

# ----------------- Task Deletion Permission Tets ---------------------------

class TaskDeletionPermissionTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.creator = User.objects.create_user(username="creator")
        cls.collaborator = User.objects.create_user(username="collaborator")
        cls.outsider = User.objects.create_user(username="outsider")

        cls.public_task = Task.objects.create(
            title="Public Task",
            creator=cls.creator,
            private=False
        )
        cls.public_task.users.add(cls.collaborator)

        cls.private_task = Task.objects.create(
            title="Private Task",
            creator=cls.creator,
            private=True
        )

    def test_outsider_cannot_delete_public_task(self):
        self.client.force_login(self.outsider)

        response = self.client.post(
            reverse("task:delete_task", args=[self.public_task.pk])
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            Task.objects.filter(pk=self.public_task.pk).exists()
        )

    def test_collaborator_cannot_delete_task(self):
        self.client.force_login(self.collaborator)

        response = self.client.post(
            reverse("task:delete_task", args=[self.public_task.pk])
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            Task.objects.filter(pk=self.public_task.pk).exists()
        )

    def test_private_task_hidden_from_outsider(self):
        self.client.force_login(self.outsider)

        url = reverse(
            "task:delete_task",
            args=[self.private_task.pk]
        )

        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(self.client.post(url).status_code, 404)

        self.assertTrue(
            Task.objects.filter(pk=self.private_task.pk).exists()
        )

    def test_creator_can_delete_task_only_via_post(self):
        self.client.force_login(self.creator)

        url = reverse(
            "task:delete_task",
            args=[self.public_task.pk]
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertTrue(
            Task.objects.filter(pk=self.public_task.pk).exists()
        )

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.assertFalse(
            Task.objects.filter(pk=self.public_task.pk).exists()
        )

    def test_missing_task_returns_404(self):
        self.client.force_login(self.creator)

        response = self.client.post(
            reverse("task:delete_task", args=[999999])
        )

        self.assertEqual(response.status_code, 404)

# ----------------- Team Update Permission Tets ---------------------------

class TeamUpdatePermissionTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.member = User.objects.create_user(username="member")
        cls.outsider = User.objects.create_user(username="outsider")

        cls.team = Team.objects.create(name="Original Team")
        cls.team.users.add(cls.member)

    def test_outsider_cannot_update_team(self):
        self.client.force_login(self.outsider)

        url = reverse("task:update_team", args=[self.team.pk])

        self.assertEqual(self.client.get(url).status_code, 403)

        response = self.client.post(url, {
            "name": "Hacked Team",
            "users": [self.outsider.pk],
        })

        self.team.refresh_from_db()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.team.name, "Original Team")
        self.assertFalse(
            self.team.users.filter(pk=self.outsider.pk).exists()
        )

    def test_member_can_update_team(self):
        self.client.force_login(self.member)

        response = self.client.post(
            reverse("task:update_team", args=[self.team.pk]),
            {
                "name": "Updated Team",
                "users": [self.member.pk, self.outsider.pk],
            }
        )

        self.team.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.team.name, "Updated Team")
        self.assertTrue(
            self.team.users.filter(pk=self.member.pk).exists()
        )
        self.assertTrue(
            self.team.users.filter(pk=self.outsider.pk).exists()
        )

    def test_missing_team_returns_404(self):
        self.client.force_login(self.member)

        response = self.client.get(
            reverse("task:update_team", args=[999999])
        )

        self.assertEqual(response.status_code, 404)

# ----------------- Team Deletition Permission Tets ---------------------------

class TeamDeletionPermissionTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.member = User.objects.create_user(username="member")
        cls.outsider = User.objects.create_user(username="outsider")
        cls.admin = User.objects.create_superuser(
            username="admin",
            password="test-password-123"
        )

        cls.team = Team.objects.create(name="Test Team")
        cls.team.users.add(cls.member)

    def test_outsider_cannot_delete_team(self):
        self.client.force_login(self.outsider)

        url = reverse("task:delete_team", args=[self.team.pk])

        self.assertEqual(self.client.get(url).status_code, 403)
        self.assertEqual(self.client.post(url).status_code, 403)

        self.assertTrue(
            Team.objects.filter(pk=self.team.pk).exists()
        )

    def test_member_can_delete_team_only_via_post(self):
        self.client.force_login(self.member)

        url = reverse("task:delete_team", args=[self.team.pk])

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Team.objects.filter(pk=self.team.pk).exists()
        )

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Team.objects.filter(pk=self.team.pk).exists()
        )

    def test_superuser_can_delete_team(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse("task:delete_team", args=[self.team.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Team.objects.filter(pk=self.team.pk).exists()
        )

    def test_missing_team_returns_404(self):
        self.client.force_login(self.member)

        response = self.client.post(
            reverse("task:delete_team", args=[999999])
        )

        self.assertEqual(response.status_code, 404)

# ------------- Regresion Tests --------------------


class TeamMembershipPermissionTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.member = User.objects.create_user(username="member")
        cls.outsider = User.objects.create_user(username="outsider")

        cls.team = Team.objects.create(name="Test Team")
        cls.team.users.add(cls.member)

    def test_outsider_cannot_join_team(self):
        self.client.force_login(self.outsider)

        response = self.client.post(
            reverse(
                "task:enter_team",
                args=[self.team.pk, self.outsider.userprofile.pk]
            )
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            self.team.users.filter(pk=self.outsider.pk).exists()
        )

    def test_outsider_cannot_remove_member(self):
        self.client.force_login(self.outsider)

        response = self.client.post(
            reverse(
                "task:leave_team",
                args=[self.team.pk, self.member.userprofile.pk]
            )
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            self.team.users.filter(pk=self.member.pk).exists()
        )

    def test_member_can_add_and_remove_user(self):
        self.client.force_login(self.member)

        enter_url = reverse(
            "task:enter_team",
            args=[self.team.pk, self.outsider.userprofile.pk]
        )

        response = self.client.post(enter_url)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            self.team.users.filter(pk=self.outsider.pk).exists()
        )

        leave_url = reverse(
            "task:leave_team",
            args=[self.team.pk, self.outsider.userprofile.pk]
        )

        response = self.client.post(leave_url)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            self.team.users.filter(pk=self.outsider.pk).exists()
        )

    def test_member_can_leave_own_team(self):
        self.client.force_login(self.member)

        response = self.client.post(
            reverse(
                "task:leave_team",
                args=[self.team.pk, self.member.userprofile.pk]
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            self.team.users.filter(pk=self.member.pk).exists()
        )

    def test_membership_changes_reject_get(self):
        self.client.force_login(self.member)

        enter_url = reverse(
            "task:enter_team",
            args=[self.team.pk, self.outsider.userprofile.pk]
        )

        leave_url = reverse(
            "task:leave_team",
            args=[self.team.pk, self.member.userprofile.pk]
        )

        self.assertEqual(self.client.get(enter_url).status_code, 405)
        self.assertEqual(self.client.get(leave_url).status_code, 405)

    def test_missing_profile_returns_404(self):
        self.client.force_login(self.member)

        response = self.client.post(
            reverse(
                "task:enter_team",
                args=[self.team.pk, 999999]
            )
        )

        self.assertEqual(response.status_code, 404)
