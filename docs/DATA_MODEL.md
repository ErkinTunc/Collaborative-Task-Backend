# Data Model

TeamForge uses Django's built-in `User` plus three models defined in `tasks/models.py`: `Task`, `Team` and `UserProfile`.

## Relationships at a glance

```text
User 1 ---- * Task         (Task.creator)
User * ---- * Task         (Task.users: assigned people)
Team * --- * Task         (Task.teams)
User * ---- * Team         (Team.users: members)
Task * --- * Task         (Task.subtasks: directed links)
User 1 ---- 1 UserProfile  (UserProfile.user)
```

The creator and assigned users are deliberately separate relationships: being assigned to work on a task does not make someone its owner.

## Task

| Field | Django type | Notes |
| --- | --- | --- |
| `creator` | `ForeignKey(User)` | Required; deleting the creator deletes the task (`CASCADE`) |
| `title` | `CharField(max_length=200)` | Required |
| `status` | `CharField` | `todo` (default), `in_progress`, `done` |
| `description` | `TextField(blank=True)` | Optional |
| `private` | `BooleanField(default=False)` | Public unless explicitly made private |
| `users` | `ManyToManyField(User)` | People assigned to the task |
| `teams` | `ManyToManyField(Team, blank=True)` | Teams assigned to the task |
| `subtasks` | `ManyToManyField('self', symmetrical=False, blank=True)` | Directed child-task links |
| `deadline` | `DateTimeField(null=True, blank=True)` | Optional |
| `created_at` | `DateTimeField(auto_now_add=True)` | Creation timestamp |
| `updated_at` | `DateTimeField(auto_now=True)` | Last save timestamp |

### Why keep creator and assignees separate?

An assignee can collaborate on a task. Its creator retains the ability to delete it. A superuser can do both. Using separate fields makes that distinction possible without inventing an owner role for every participant.

### What does a subtask link mean?

`parent.subtasks.add(child)` creates a one-way relation. It does not automatically copy the parent's privacy flag, members, team assignments or edit permissions to the child. Each task has its **own** access rules, and the task detail view only shows linked subtasks the viewer is allowed to see.

The model does **not** enforce an acyclic tree. A task can have multiple parents, and no cycle prevention is implemented. Do not treat this as a validated project-planning hierarchy.

## Team

| Field | Django type | Notes |
| --- | --- | --- |
| `name` | `CharField(max_length=100)` | Team name |
| `users` | `ManyToManyField(User)` | Members |

A team is both a collaboration group and an access group. Membership in a team assigned to a task allows that member to see and edit the task, including private tasks.

There is **no team owner field**. All members can manage membership and delete the team under the current permission policy. A team's creator is simply added as one of its members.

## User and UserProfile

Django's default `User` stores identity and authentication data. TeamForge has not replaced it with a custom user model.

| `UserProfile` field | Django type | Notes |
| --- | --- | --- |
| `user` | `OneToOneField(User)` | Profile is removed when user is deleted (`CASCADE`) |
| `description` | `TextField(blank=True)` | Optional biography |
| `image` | `ImageField` | Default `profile_pictures/placeholder.png` |

A `post_save` signal creates a `UserProfile` when a `User` is first created.

The image field stores a **relative file path**, not the image bytes in SQLite. Files live under `pictures/profile_pictures/` (`MEDIA_ROOT` + `upload_to`). `.png`, `.webp` and other accepted image formats are possible; it is not PNG-only.

## Deletion and data integrity

- Deleting a **user** deletes their profile and tasks they created because of `CASCADE`. Their many-to-many memberships/assignments are also removed.
- Deleting a **team** removes its task links but does not delete the linked tasks.
- Deleting a **task** removes its assignment and subtask relations. It does not automatically delete its linked child tasks.
- The model defines `post_delete` handlers that clear related many-to-many fields, although Django already cleans up these join rows during deletion.

This matters when deciding whether a collaboration app should preserve tasks after someone closes their account. The current model does **not** preserve tasks owned by a deleted user.

See [Permissions](PERMISSIONS.md) for the rules applied before these operations.
