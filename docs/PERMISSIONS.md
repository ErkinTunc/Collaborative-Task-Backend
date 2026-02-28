# Permissions Model

This document describes the authorization rules currently enforced in the application.

Permissions are implemented explicitly at the view level.

There is no separate permission layer or service abstraction.

---

## 1. Authentication

- Most routes are protected using `@login_required`.
- Unauthenticated users are redirected to the login page.
- Registration and login routes are accessible only to unauthenticated users.

---

## 2. Superuser Privileges

A Django superuser can:

- Access the control panel
- Create users
- Update or delete any user
- Update or delete any team
- Update or delete any task

Superuser checks are performed using:

```bash
request.user.is_superuser
```

---

## 3. Task Permissions

### Task Creation

- Any authenticated user can create a task.
- The creator field is automatically set to the current user.

---

### Task Update

A task can be updated if the user is:

- The task creator
- Directly assigned to the task
- A member of a team assigned to the task
- A superuser

This logic is enforced in `update_task`.

---

### Subtask Creation

A subtask can be created under a task if the user is:

- The task creator
- Directly assigned to the task
- A member of a team assigned to the task
- A superuser

This logic is enforced in `create_sub_task`.

---

### Add Team to Task

A new team can be created and attached to a task if the user is:

- The task creator
- Directly assigned to the task
- A member of a team assigned to the task
- A superuser

This logic is enforced in `create_sub_team`.

---

### Task Deletion

A task can be deleted only if:

- The user is the task creator
- OR the user is a superuser

Being an assigned collaborator is not sufficient.

This logic is enforced in `delete_task`.

---

## 4. Team Permissions

### Team Creation

- Any authenticated user can create a team.

---

### Team Update

A team can be updated if the user is:

- A member of that team
- OR a superuser

Enforced in `update_team`.

---

### Team Deletion

A team can be deleted if the user is:

- A member of that team
- OR a superuser

Enforced in `delete_team`.

---

### Join / Leave Team

- Joining and leaving teams are done via POST routes.
- The current implementation allows adding or removing a user from a team via the route parameters.
- No additional restriction is enforced beyond authentication.

Enforced in `enter_team` and `leave_team`.

---

## 5. User Permissions

### View Profile

- Any authenticated user can view any user profile.

---

### Create User

- Only a superuser can create a new user.

Enforced in `create_user`.

---

### Update Profile

A profile can be updated if:

- The logged-in user owns that profile
- OR the user is a superuser

Enforced in `update_user`.

---

### Delete User

A user account can be deleted if:

- The logged-in user owns that profile
- OR the user is a superuser

Enforced in `delete_user`.

Deletion removes the Django `User` instance.

---

## Summary

Permissions in this project are:

- Explicit
- View-level
- Condition-based
- Superuser-aware

There is no centralized permission system.
All authorization logic is visible directly in the view functions.
