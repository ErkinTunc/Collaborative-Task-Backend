
from django.db.models import Q
from .models import Task


def visible_tasks_for(user):
    """
    Return tasks the user is allowed to view.
    """
    if not user.is_authenticated:
        return Task.objects.none()

    if user.is_superuser:
        return Task.objects.all()

    return Task.objects.filter(
        Q(private=False)
        | Q(creator=user)
        | Q(users=user)
        | Q(teams__users=user)
    ).distinct()


def can_edit_task(user, task):
    """
    Check whether the user can modify a task.
    """
    if not user.is_authenticated:
        return False

    if user.is_superuser or task.creator_id == user.pk:
        return True

    return (
        task.users.filter(pk=user.pk).exists()
        or task.teams.filter(users=user).exists()
    )
