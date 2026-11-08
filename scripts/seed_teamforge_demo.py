"""Seed a newly migrated TeamForge SQLite database with fictional demo records.

From the project root, run:
    python manage.py shell -c "exec(open('scripts/seed_teamforge_demo.py', encoding='utf-8').read())"

Requirements:
    - Run migrations first.
    - An existing superuser is allowed, but the database must contain no
      regular users, teams, or tasks. Nothing will be removed by this script.
    - Demo users have unusable passwords. Set a password explicitly for any
      account you need to log into (e.g. `python manage.py changepassword Mr.White`).
    - Optional portraits belong under MEDIA_ROOT/profile_pictures/mr_white.png
      (or .jpg/.jpeg/.webp). Existing files are linked; no images are generated.
"""

from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from tasks.models import Task, Team

# Username, first name, last name, description for UserProfile.
# Dots are valid in Django usernames. Django templates currently show `username`,
# so these will appear as Mr.White, Mr.Pink, etc.
PEOPLE = [
    ("Mr.White", "Mr", "White", "Alfa operations coordinator. Oversees the release plan."),
    ("Mr.Pink", "Mr", "Pink", "Coordinates interface work and sprint tasks."),
    ("Mr.Brown", "Mr", "Brown", "Maintains documentation and onboarding workflows."),
    ("Mr.Orange", "Mr", "Orange", "Supports verification and integration checks."),
    ("Mr.Blue", "Mr", "Blue", "Reviews quality and regression testing."),
    ("Mr.Blonde", "Mr", "Blonde", "Focuses on access control and deployment readiness."),
]

TEAMS = {
    "Alfa": ["Mr.White", "Mr.Pink", "Mr.Blonde"],
    "Beta": ["Mr.Pink", "Mr.Brown", "Mr.Orange"],
    "Teta": ["Mr.White", "Mr.Orange", "Mr.Blue"],
}

# Title, status, private, creator, assigned usernames, team, deadline days, description.
TASKS = [
    (
        "Operation Atlas: Demo release", "in_progress", False,
        "Mr.White", ["Mr.Pink"], "Alfa", 14,
        "Coordinate the TeamForge portfolio walkthrough and verify the main task workflow.",
    ),
    (
        "Prepare mission dashboard", "done", False,
        "Mr.Pink", ["Mr.Brown"], "Beta", 5,
        "Review task cards, status indicators and the team overview for the demo.",
    ),
    (
        "Publish onboarding guide", "todo", False,
        "Mr.Brown", ["Mr.Orange"], "Beta", 10,
        "Write clear instructions for account registration and first task creation.",
    ),
    (
        "Verify launch checklist", "in_progress", False,
        "Mr.Blue", ["Mr.Orange"], "Teta", 9,
        "Check the core user flows and record any issues before release.",
    ),
    (
        "Capture product walkthrough", "todo", False,
        "Mr.Pink", ["Mr.Brown"], "Beta", 16,
        "Record a short task creation and status update demo for the README.",
    ),
    (
        "Audit object-level permissions", "in_progress", True,
        "Mr.White", ["Mr.Blonde"], "Alfa", 6,
        "Validate creator, collaborator and team-based access rules for private tasks.",
    ),
    (
        "Review team membership policy", "done", True,
        "Mr.Blonde", ["Mr.Pink"], "Alfa", 4,
        "Document the trusted-team model and the implications of inviting members.",
    ),
    (
        "Test private task visibility", "todo", True,
        "Mr.White", ["Mr.Blonde"], "Alfa", 8,
        "Confirm that an unrelated account receives a 404 for a private task.",
    ),
    (
        "Run authorization regression tests", "in_progress", True,
        "Mr.Orange", ["Mr.Blue"], "Teta", 7,
        "Exercise allowed and forbidden requests and verify the expected responses.",
    ),
    (
        "Investigate login edge cases", "todo", True,
        "Mr.Orange", ["Mr.Blue"], "Teta", 11,
        "Check incorrect credentials, redirects and session handling.",
    ),
    (
        "Review profile image handling", "todo", True,
        "Mr.Brown", ["Mr.Pink"], "Beta", 12,
        "Validate that profile pictures are stored as media and served correctly.",
    ),
    (
        "Prepare deployment configuration", "in_progress", True,
        "Mr.Blonde", ["Mr.White"], "Alfa", 13,
        "Review HTTPS, environment variables, static files and media paths on alwaysdata.",
    ),
]

CHILDREN = [
    "Prepare mission dashboard",
    "Publish onboarding guide",
    "Verify launch checklist",
]


def maybe_set_portrait(profile, username):
    """Link an existing image under MEDIA_ROOT; otherwise keep the model default."""
    stem = username.lower().replace(".", "_")
    folder = Path(settings.MEDIA_ROOT) / "profile_pictures"
    for extension in (".png", ".jpg", ".jpeg", ".webp"):
        photo = folder / f"{stem}{extension}"
        if photo.is_file():
            profile.image.name = f"profile_pictures/{photo.name}"
            profile.save(update_fields=["image"])
            return True
    return False


@transaction.atomic
def seed():
    User = get_user_model()

    # Fail closed: never merge this fixture with existing regular user data.
    if (
        User.objects.filter(is_superuser=False).exists()
        or Team.objects.exists()
        or Task.objects.exists()
    ):
        raise RuntimeError(
            "Expected an empty demo database (superusers are allowed). "
            "No changes were made. Back up and reset only the intended local DB first."
        )

    users = {}
    portraits = 0
    for username, first_name, last_name, bio in PEOPLE:
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=f"{username.lower()}@example.invalid",
            password=None,
        )
        # The project's post_save signal automatically creates UserProfile.
        user.userprofile.description = bio
        user.userprofile.save(update_fields=["description"])
        portraits += maybe_set_portrait(user.userprofile, username)
        users[username] = user

    teams = {}
    for name, member_names in TEAMS.items():
        team = Team.objects.create(name=name)
        team.users.add(*(users[username] for username in member_names))
        teams[name] = team

    tasks = {}
    now = timezone.now()
    for title, status, private, creator, assigned, team_name, days, description in TASKS:
        task = Task.objects.create(
            title=title,
            creator=users[creator],
            status=status,
            private=private,
            description=description,
            deadline=now + timedelta(days=days),
        )
        task.users.add(*(users[username] for username in assigned))
        task.teams.add(teams[team_name])
        tasks[title] = task

    tasks["Operation Atlas: Demo release"].subtasks.add(
        *(tasks[title] for title in CHILDREN)
    )

    print("TeamForge demo database seeded successfully.")
    print(f"Regular users: {len(users)} (password login DISABLED until set explicitly)")
    print(f"Teams: {Team.objects.count()}")
    print(f"Tasks: {Task.objects.count()}")
    print(f"Public: {Task.objects.filter(private=False).count()}")
    print(f"Private: {Task.objects.filter(private=True).count()}")
    print(f"Parent-child links: {len(CHILDREN)}")
    print(f"Existing portraits linked: {portraits}/{len(PEOPLE)}")
    print("For a screenshot account: python manage.py changepassword Mr.White")


seed()
