# Data Models (Entities)

This section describes the core entities of the system and the reasoning behind their relationships.

---

## Task

```bash
{
  "private": boolean,
  "creator": User,

  "title": string,
  "status": "todo" | "in_progress" | "done",
  "description": string,

  "users": [User],     // List of users assigned to this task
  "teams": [Team],     // List of teams associated with this task
  "subtasks": [Task],  // Child tasks (self-referencing relationship)

  "created_at": Date,
  "updated_at": Date,
  "deadline": Date
}
```

### Modeling Decisions

#### 1. Creator vs Assigned Users

The `creator` field is separated from the `users` many-to-many field.

##### Reason

- The creator represents ownership.
- Assigned users represent collaboration.
- Deletion permissions depend on ownership, not assignment.
- A creator may not necessarily be the only collaborator.

This separation enables explicit and fine-grained authorization logic.

---

#### 2. Self-Referencing Many-to-Many (Subtasks)

`subtasks` uses a directed self-referencing `ManyToMany` relationship.

##### Reason

- Allows hierarchical decomposition of work.
- Supports flexible task structures.
- Enables non-symmetrical parent → child relationships.

This models a directed graph rather than a strict tree structure.

No cycle detection is implemented; graph integrity is handled at the application level.

---

#### 3. Teams and Visibility Propagation

Tasks can be linked to teams.

##### Reason

- Teams act as permission groups.
- If a user belongs to a team assigned to a task, they inherit visibility and modification rights.
- Avoids duplicating user-task assignments for every team member.

This design enables scalable and centralized collaboration management.

## Team

```bash
{
  "name": string,
  "users": [User]  // Members of the team
}
```

### Modeling Decision

Teams serve two roles:

1. Organizational grouping
2. Permission propagation unit

Tasks reference teams rather than duplicating individual team members.

#### Reason

- Centralizes permission logic at the team level.
- Prevents redundant user-task assignments.
- Ensures that changes in team membership automatically affect task visibility.
- Maintains consistency between collaboration structure and access control.

## User

```bash

{
  "id": int,
  "username": string,
  "email": string,
  "password": string
}
```

### Modeling Decision

The built-in Django `User` model is used.

#### Reason

- Avoids reimplementing authentication logic.
- Leverages Django’s built-in password hashing and validation system.
- Maintains full compatibility with Django’s authentication framework.

## UserProfile

```bash
{
  "user": User,        // One-to-one relationship with User
  "description": string,
  "image": *.png       // Stored in the "pictures/profile_pictures" directory
}
```

### Modeling Decision

`UserProfile` extends Django’s built-in `User` model using a `OneToOneField`.

#### Reason

- Keeps authentication logic separate from profile-related data.
- Avoids modifying Django’s core `User` model.
- Allows additional fields (e.g., `description`, `image`) without implementing a custom user model.
- Maintains compatibility with Django’s built-in authentication system.

The `UserProfile` instance is automatically created via a Django signal when a new `User` is created.
