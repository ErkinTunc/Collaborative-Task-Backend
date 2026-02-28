# Architecture

## App Separation

I split the project into two Django apps:

- `users/` → authentication (register, login, logout)
- `tasks/` → core domain (Task, Team, UserProfile + views + permissions)

Reason: keep auth separated so the domain logic does not depend on authentication internals.

---

## URL Routing

Routing is explicit:

- `task_manager/urls.py` defines auth routes (`/register/`, `/login/`, `/logout/`)
- all domain routes are delegated to the `tasks` app (`include("tasks.urls")`)

Goal: every URL can be traced directly to a view with no hidden routing abstraction.

---

## Data Modeling

Core entities:

- `Task`
- `Team`
- `UserProfile`

Modeling choices:

- Many-to-Many: `Task ↔ Users`
- Many-to-Many: `Task ↔ Teams`
- Self-referencing Many-to-Many for subtasks:
  - `subtasks = ManyToMany('self', symmetrical=False)`
  - allows directed task → subtask relationships
- `creator` field on Task to enforce ownership rules
- `UserProfile` extends Django `User` with a One-to-One relationship

---

## Signals (Lifecycle Automation)

I use signals only for lifecycle consistency:

1. Auto-create `UserProfile` when a Django `User` is created.
2. Cleanup Many-to-Many relations when:
   - a User is deleted
   - a Team is deleted
   - a Task is deleted

Reason: deletions can happen from views, admin, or Django shell — signals enforce cleanup regardless of entry point.

---

## Authorization Strategy

Authorization is enforced directly in the views (`tasks/views.py`).

Examples:

- Only superusers can access the admin control panel.
- Only task creators (or superusers) can delete tasks.
- Updating tasks requires collaboration rights.
- Updating/deleting teams requires membership (or superuser).
- Updating/deleting user profiles requires ownership (or superuser).

Reason: in a server-rendered Django app, the view is the request boundary, so permission checks stay explicit and hard to bypass.

---

## Why No Service Layer / Why No DRF (Scope Decision)

I kept the architecture minimal because:

- it’s a single server-rendered interface
- workflows are not complex enough to justify extra layers
- adding a service layer or DRF would add indirection without strong payoff at this scope

Trade-off: views are larger, but the code stays easy to audit.