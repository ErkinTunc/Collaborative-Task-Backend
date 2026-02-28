# Testing Strategy

At this stage, validation has been performed manually on the running application (development server).

Authentication flows, visibility rules, permission checks, and deletion behavior were tested using different user roles (creator, collaborator, team member, outsider, superuser).

The core complexity of this system lies in enforcing correct visibility and object-level authorization.

The goal of testing is to ensure:

- access rules cannot be bypassed,
- private data is not exposed,
- relational integrity is preserved after deletions.

The sections below outline the intended automated testing strategy.
---

## 1. What Should Be Tested

### 1.1 Authentication Gate

**Goal:** Anonymous users must not access protected pages.

Test cases:
- Unauthenticated request to `/` redirects to `/login/`
- Unauthenticated request to `/tasks/:id/` redirects to `/login/`
- Unauthenticated request to `/teams/:id/` redirects to `/login/`

Why it matters:
- prevents unintended public exposure.

---

### 1.2 Task Visibility Rules

**Goal:** Users should only see tasks they are allowed to see.

Test cases:
- Public task visible to all authenticated users
- Private task visible to:
  - creator
  - assigned users
  - members of assigned teams
  - superuser
- Private task NOT visible to unrelated users

Why it matters:
- this is the main privacy guarantee of the system.

---

### 1.3 Object-Level Authorization (Update/Delete)

**Goal:** Users cannot modify or delete objects they do not have rights to.

Task tests:
- Only creator (or superuser) can delete a task
- Only collaborator (creator / assigned / team-member / superuser) can update a task

Team tests:
- Only team members (or superuser) can update/delete a team

User profile tests:
- Only profile owner (or superuser) can update/delete a profile

Why it matters:
- prevents horizontal privilege escalation.

---

### 1.4 Subtask Linking Integrity

**Goal:** Only authorized users can create subtasks under a task.

Test cases:
- Authorized collaborator can create subtask via `/tasks/:id/add-sub-task`
- Unauthorized user receives rejection (no creation)

Why it matters:
- subtasks inherit the parent task’s permission surface.

---

### 1.5 Signals / Cleanup on Deletion

**Goal:** Deleting an entity clears many-to-many relations to prevent dangling relations.

Test cases:
- Deleting a user clears user↔tasks and user↔teams relationships
- Deleting a team clears team↔tasks relationships
- Deleting a task clears task↔users and task↔teams relationships

Why it matters:
- ensures consistent database state even if deletion occurs from admin panel or shell.

---

## 2. How To Implement (Django Approach)

Recommended tools:

- `django.test.TestCase`
- Django test client (`self.client`)
- Fixtures created in `setUp()`

Common pattern:

1. Create users: creator / collaborator / outsider / superuser
2. Create team and attach users
3. Create tasks:
   - public task
   - private task assigned to user
   - private task assigned to team
4. Use `self.client.force_login(user)`
5. Perform GET/POST to the view
6. Assert:
   - HTTP status / redirect behavior
   - database objects count unchanged/changed
   - relations exist/removed

---

## 3. Suggested Test File Organization

- `tasks/tests/test_visibility.py`
- `tasks/tests/test_permissions.py`
- `tasks/tests/test_signals.py`
- `users/tests/test_auth_flow.py`

This keeps tests grouped by system risk, not by model.

---

## 4. Current Status

At the moment, automated tests are not implemented.

However, the system’s architecture and documentation are designed to make permission rules explicit and testable, and the test plan above outlines the intended validation strategy.