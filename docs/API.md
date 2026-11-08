# HTTP Routes

TeamForge uses Django templates and HTML forms. These are **server-rendered routes, not a JSON REST API**. Form submissions normally redirect back to a page; there is no DRF or OpenAPI interface.

The route paths below come from `task_manager/urls.py` and `tasks/urls.py`. A path without a final slash is intentionally shown that way.

## Pages and authentication

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/` | Dashboard: your tasks, your teams, and public tasks |
| GET | `/control-panel/` | Admin overview of tasks, teams, and users (superuser only) |
| GET, POST | `/register/` | Register a user |
| GET, POST | `/login/` | Sign in |
| POST | `/logout/` | Sign out |
| GET | `/admin/` | Built-in Django admin (subject to Django admin permissions) |

Most domain routes require login. Anonymous requests are redirected to `/login/`. The control panel is restricted to superusers, although the current view returns a plain-text HTTP 200 response when a non-superuser visits it; this should eventually be changed to HTTP 403.

## Users and profiles

| Method | Path | Access / behavior |
| --- | --- | --- |
| GET | `/users/<id>/` | Any signed-in user can view a profile; associated tasks are filtered by the viewer's permissions |
| GET, POST | `/users/add` | Superuser creates an account |
| GET, POST | `/users/update/<id>/` | Profile owner or superuser edits account details, description, and image |
| GET, POST | `/users/delete/<id>/` | Profile owner or superuser; GET displays confirmation, POST deletes |

**ID detail:** In these routes, `id` refers to `UserProfile.pk`, not necessarily `User.pk` (including the add/remove team membership routes below).

## Teams

| Method | Path | Access / behavior |
| --- | --- | --- |
| GET | `/teams/<id>/` | Any signed-in user can view team details; task list respects task visibility |
| GET, POST | `/teams/add` | Any signed-in user can create a team and becomes a member |
| GET, POST | `/teams/update/<id>/` | A team member or superuser can edit name and membership |
| GET, POST | `/teams/delete/<id>/` | A team member or superuser; GET confirms, POST deletes |
| POST | `/teams/<team_id>/enter/<user_id>/` | A member or superuser adds the user identified by **profile ID** |
| POST | `/teams/<team_id>/leave/<user_id>/` | A member or superuser removes a user; a user may also remove themselves |

The `enter` and `leave` handlers use `@require_POST`: GET requests are not accepted. There is no separate team owner role.

## Tasks

| Method | Path | Access / behavior |
| --- | --- | --- |
| GET | `/tasks/<id>/` | View a public task or a private task you are authorized to see |
| GET, POST | `/tasks/add` | Create a task; the logged-in user becomes its creator |
| GET, POST | `/tasks/update/<id>/` | Creator, assigned user, member of an assigned team, or superuser |
| GET, POST | `/tasks/delete/<id>/` | Creator or superuser; GET confirms, POST deletes |
| GET, POST | `/tasks/<id>/add-sub-task` | Authorized task editor creates and links a child task |
| GET, POST | `/tasks/<id>/add-sub-team` | Authorized task editor creates and attaches a team |

Task forms accept a title, privacy flag, status, optional description and deadline, assigned users, and assigned teams. Team choices are limited in `TaskForm`: regular users can choose their own teams when creating a task, and can also retain teams already linked to an existing task when editing it. Superusers can choose any team.

## Errors and form behavior

- Private tasks that a user cannot see return **404** on the detail and protected update/delete paths.
- A visible task that the user cannot edit or delete generally returns **403**.
- Forbidden team changes return **403**; unauthenticated users are redirected to login.
- Some older profile and admin handlers still return plain-text **200** on unauthorized access. The responses are not consistent yet.
- POST forms use Django CSRF protection. Do not treat these endpoints as a public programmatic API.

See [Permissions](PERMISSIONS.md) for the full access rules and [Security](SECURITY.md) for known limitations.
