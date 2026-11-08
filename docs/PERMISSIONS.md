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

The application follows an **equal-permission team membership model**. There is no separate team owner or team administrator role.

### Team Creation

- Any authenticated user can create a team.
- The creator is automatically added as a team member.

---

### Team Update

A team can be updated by:

- Any member of that team
- A superuser

Authorized users can change the team name and manage its members.

Enforced in `update_team`.

---

### Team Deletion

A team can be deleted by:

- Any member of that team
- A superuser

Deletion requires a POST request. A GET request only displays the confirmation page.

Enforced in `delete_team`.

---

### Team Membership Management

**Adding users:**

- Any team member or superuser can add users to the team.
- Users cannot join a team themselves unless they are already members or superusers.

**Removing users:**

- Any team member or superuser can remove other users.
- Users can remove themselves from a team.

Membership changes through `enter_team` and `leave_team` require POST requests.

Team members and superusers can also manage membership through `update_team`.

---

### Security Trade-off

Team membership grants access to private tasks assigned to that team. Members can also edit tasks assigned to their team.

Because team members can add other users, they can extend access to these private tasks.

This behavior is intentional for a **trusted, collaborative team model**.

The application does not currently implement separate team owner or administrator roles. Therefore, every team member has permission to manage membership and delete the team.

This design is suitable for a trusted collaborative environment, but it is not intended to enforce isolation between untrusted team members.

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

