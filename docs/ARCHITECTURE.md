# Architecture

TeamForge is a small, server-rendered Django application. The goal was to keep the code straightforward while making permission checks hard to overlook.

## Request flow

```text
Browser
  -> task_manager/urls.py
  -> tasks/urls.py or users/views.py
  -> Django view + form validation
  -> permission checks + Django ORM
  -> SQLite
  -> Django template / redirect
```

The browser submits HTML forms; the application does not expose a JSON REST API. Bootstrap and a small CSS file handle the interface.

## App layout

| Location | Responsibility |
| --- | --- |
| `users/` | Registration and login views; registration form |
| `tasks/models.py` | Task, Team, UserProfile and lifecycle signals |
| `tasks/views.py` | Dashboard, profiles, teams, tasks and control panel |
| `tasks/forms.py` | Task, team and profile forms, including allowed team selections |
| `tasks/permissions.py` | Shared task visibility and edit checks |
| `tasks/tests.py` | Automated authorization tests |
| `task_manager/` | Settings and top-level URLs |

An intentional historical detail: `UserProfile` lives in `tasks/models.py`, not in the `users` app. The app split is practical, not a claim that the domains are perfectly isolated.

## Data relationships

- A task has one **creator** (`ForeignKey(User)`), distinct from the users assigned to it.
- Users and teams can each be assigned to multiple tasks through many-to-many relations.
- Teams contain multiple users; membership determines access to private tasks linked to the team.
- A task can link to other tasks through a **directed** self-referencing many-to-many relation (`symmetrical=False`). This is a graph, not a guaranteed tree: multiple parents and cycles are not prevented by the model.
- `UserProfile` adds a description and image to Django's built-in user account.

See [Data Model](DATA_MODEL.md) for the fields and deletion behavior.

## Authorization: shared helpers, explicit views

Two helpers in `tasks/permissions.py` reduce duplication:

- `visible_tasks_for(user)` returns public tasks and private tasks visible through creation, direct assignment, team membership, or superuser status.
- `can_edit_task(user, task)` checks whether the user is the creator, an assigned user, a member of an assigned team, or a superuser.

Task detail, edit and delete handlers use these helpers. The **delete** rule is deliberately narrower than the edit rule: only the creator or superuser may delete a task. Team membership and profile ownership checks remain in their respective views.

`TaskForm` also limits which teams a user can attach to a task. Existing team links are preserved as available choices on an edit even if the editor is not a member of those teams.

For exact behavior, see [Permissions](PERMISSIONS.md).

## Why this structure?

There is no service layer or Django REST Framework. For this size of project, views, model forms and two permission helpers are enough. Adding extra layers now would mostly move the same logic into more files.

The trade-off is that some views mix request handling and business rules. As workflows grow, those pieces may deserve dedicated services or more reusable policies.

## Signals and deletion behavior

A `post_save` signal creates a profile when a user is created. There are also `post_delete` receivers calling `.clear()` on related many-to-many fields.

Django already cleans up many-to-many join records when referenced objects are deleted, so those `.clear()` handlers are mostly redundant rather than a separate integrity mechanism. More important: `Task.creator` has `on_delete=models.CASCADE`. **Deleting a user also deletes tasks they created**, not just their profile or assignments. This is an intentional consequence of the current schema and something to reconsider before handling real user data.

## Static files, media and deployment

- SQLite is configured in `task_manager/settings.py`.
- WhiteNoise serves collected **static** assets; it does not by itself serve uploaded profile pictures.
- Profile images use `MEDIA_ROOT = pictures/` and `MEDIA_URL = /pictures/`. Local media URLs work through Django's development routing when `DEBUG=True`; production media needs separate hosting configuration.
- `DJANGO_SECRET_KEY` is required. `DJANGO_DEBUG=1` and `DJANGO_LOCAL_HTTP=1` are local-development options, not production settings.

See [Security](SECURITY.md) for the risks and deployment checklist.
