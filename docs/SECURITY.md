# Security Notes

TeamForge is an educational Django project with explicit authorization rules. This document records the protections in the code **and their limits**. It is not a security audit or a claim that the app is production-ready.

## What the current code does

**Authentication.** The core task, team and profile views use `@login_required`; registration and login are available to anonymous visitors. Django manages password hashing, sessions and password validators.

**Task authorization.** `tasks/permissions.py` limits visibility of private tasks to their creators, direct assignees, members of assigned teams and superusers. Editing uses a separate check; deleting is limited to the creator or superuser. The team selection in `TaskForm` also prevents normal users from attaching unrelated teams.

**Team authorization.** Membership controls editing and deletion. Membership additions and removals are POST-only and check the acting user. Team members can manage other members, by design.

**Profiles.** Any signed-in user may view another profile, but only its owner or a superuser may update or delete it.

**CSRF.** Django's `CsrfViewMiddleware` is enabled and the application uses server-rendered forms. State-changing requests should be submitted with valid CSRF tokens. This is distinct from object-level permission checking: a valid CSRF token does not grant permission.

## What is still limited

| Area | Current limitation / consequence |
| --- | --- |
| Team roles | Any member can add members and delete the team. A newly added member may gain access to private team tasks. |
| HTTP status codes | Some denied admin/profile operations return HTTP 200 with an error message instead of HTTP 403. |
| User deletion | `Task.creator` uses `CASCADE`, so deleting a user deletes tasks they created. |
| Subtasks | No cycle detection; child tasks do not inherit the parent's authorization settings automatically. |
| Test coverage | 21 automated tests concentrate on several authorization flows, not every route or security concern. |
| Rate limiting | The repository does not implement dedicated login or registration rate limits. |
| Media uploads | User profile images require appropriate upload limits, validation and safe hosting. WhiteNoise is for static assets, not uploaded media. |
| Public sample database | `db.sqlite3` is committed as demo data. It contains account records and password hashes; never place real credentials or private user information in it. |

A missing profile in `delete_user` is fetched with `.get()` rather than `get_object_or_404`, so that endpoint can also produce an unexpected server error for a nonexistent ID. This is an error-handling gap, not a documented 404 guarantee.

## Environment settings

Current settings in `task_manager/settings.py`:

- `DJANGO_SECRET_KEY` must be supplied through the environment; do not commit a real secret.
- `DJANGO_DEBUG=1` turns debug mode on. Leave it **unset** on production.
- `DJANGO_LOCAL_HTTP=1` allows local HTTP cookies by disabling the Secure flag for session and CSRF cookies. Leave it **unset** on production.
- `ALLOWED_HOSTS` lists localhost and the configured alwaysdata host. This is not a substitute for a full deployment review.
- SQLite is the configured database. The repository does not establish a PostgreSQL deployment.

### Static versus uploaded files

WhiteNoise handles static files such as CSS and icons. Profile pictures live under `pictures/` (`MEDIA_ROOT`) and are addressed by `/pictures/` (`MEDIA_URL`). Django's `static(..., document_root=...)` helper only serves these through the development server when debug mode is enabled. Production hosting must handle media separately.

Do not assume profile images are private merely because the profile page needs login: a public media server may serve the image URL directly.

## Before exposing an instance to real users

1. Remove or isolate demo accounts and database content; use unique passwords and a fresh secret key. Remember that removing data in a later commit does not erase it from Git history.
2. Keep debug and local-HTTP flags off; verify HTTPS, secure cookies, host/CSRF settings and reverse-proxy configuration.
3. Configure media serving and uploads safely, including file limits and appropriate permissions.
4. Add consistent 403/404 responses and tests for all sensitive routes, including profiles and object-level reads.
5. Review the equal-permission team model and account-deletion cascade against real product requirements.
6. Add rate limiting, logging/monitoring, backups and deployment checks. Run `python manage.py check --deploy` in the target environment and review its warnings.

See [Permissions](PERMISSIONS.md), [Testing](TESTING.md) and [Architecture](ARCHITECTURE.md) for implementation details.
