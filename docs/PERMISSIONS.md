# Permissions

This document describes what the **current Django views** permit. Authentication alone does not mean a user can edit or delete every object they can see.

## Task access

| Action | Creator | Assigned user | Member of assigned team | Superuser | Other signed-in user |
| --- | --- | --- | --- | --- | --- |
| View public task | Yes | Yes | Yes | Yes | Yes |
| View private task | Yes | Yes | Yes | Yes | No |
| Edit task | Yes | Yes | Yes | Yes | No |
| Delete task | Yes | No | No | Yes | No |

The task's `creator` and the users in `task.users` are different fields. Being assigned to a task grants editing rights but **not** deletion rights.

Task creation is allowed for any signed-in user. The creator is set on the server from `request.user`, not trusted from a form field.

### Where the checks happen

`tasks/permissions.py` contains:

- `visible_tasks_for(user)` — public tasks plus tasks visible through creator, direct assignment, assigned-team membership or superuser rights.
- `can_edit_task(user, task)` — creator, direct assignee, assigned-team member or superuser.

`detail_task`, `update_task` and `delete_task` start from the visible-task queryset. Someone who cannot see a private task receives a **404**; someone who can see but cannot perform a protected operation generally receives a **403**.

The dashboard shows your own/assigned/team tasks and public tasks as separate lists; a task may appear in both.

### Assigning teams

`TaskForm` restricts a regular user's available teams:

- On creation: teams they belong to.
- On update: teams they belong to **or** teams already linked to that task, so existing assignments can be retained.
- Superuser: all teams.

This blocks a user from adding an unrelated team to a task by submitting a crafted team ID. Assigned **individual users**, however, are selected from all users in the current form; there is no same-team restriction on individual assignment.

### Subtasks and attached teams

A user who can edit the parent task may use its `add-sub-task` or `add-sub-team` page. A new child task has its own creator, privacy and assignments; it does **not** automatically inherit all of the parent task's access rules. The task detail page filters child links to those visible to the viewer.

## Team access

Any signed-in user can view a team detail page. Its task list is filtered to tasks the viewer may see.

| Action | Who may do it? |
| --- | --- |
| Create a team | Any signed-in user; automatically becomes a member |
| Rename/update a team | A member or superuser |
| Delete a team | A member or superuser |
| Add a user to a team | A member or superuser |
| Remove another user | A member or superuser |
| Leave a team oneself | That user |

Membership updates through `/teams/<team_id>/enter/<user_id>/` and `/teams/<team_id>/leave/<user_id>/` require **POST**. The user ID in these URL patterns resolves a `UserProfile.pk`.

### The deliberate trade-off

There is no owner/admin role within a team. **Every member has equal management rights**, including the ability to add members and delete the team. Adding a member may also give them access to private tasks assigned to that team.

That is a simple model for trusted collaborators. It is **not appropriate for teams of mutually untrusted users** without stronger role and invitation controls.

## Profiles and administration

| Action | Access |
| --- | --- |
| View a user's profile | Any signed-in user; task list is visibility-filtered |
| Edit profile | Profile owner or superuser |
| Delete account | Account owner or superuser |
| Create user through `/users/add` | Superuser |
| Visit `/control-panel/` | Superuser |

Django authentication is required for the core pages. The `users` app handles registration and login; Django's built-in logout view handles logout.

**Current inconsistency:** Some older profile/admin views respond to unauthorized requests with plain-text HTTP **200** instead of **403**. The operation is blocked, but the response code should be improved. Task and team permissions generally use `PermissionDenied` for 403.

## Deletion rules

Task, team and profile deletion views show a confirmation page on **GET** and perform deletion on **POST**. Deleting a user also deletes tasks where they are the creator because the model uses `on_delete=CASCADE`.

## Tests

There are 21 tests in `tasks/tests.py`, with strongest coverage around task-team form restrictions, task deletion, team edit/delete and membership changes. They do **not** provide full coverage of all the visibility and profile rules above.

See [Testing](TESTING.md) and [Security](SECURITY.md).
