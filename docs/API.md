# API Documentation

> Note: This project is server-rendered (Django templates).  
> These routes are HTTP endpoints, not a REST API with JSON responses.

## Home

- `GET /` – Displays all public tasks and the current user's tasks
- `GET /control-panel/` – Superuser control panel. Displays all tasks, teams, and users.

## Authentication

- `GET /register/` – Registration page
- `POST /register/` – Create a new account
- `GET /login/` – Login page
- `POST /login/` – Log in
- `POST /logout/` – Log out

## User

- `GET /users/:id/` – View a user's profile, including their tasks and teams
- `POST /users/add` – Create a new user (superuser only)
- `POST /users/update/:id/` – Update a user profile (owner or superuser)
- `POST /users/delete/:id/` – Delete a user (owner or superuser)

## Team

- `GET /teams/:id/` – View a team profile
- `POST /teams/add` – Create a team
- `POST /teams/update/:id/` – Update a team (member or superuser)
- `POST /teams/delete/:id/` – Delete a team (member or superuser)
- `POST /teams/:team_id/enter/:user_id/` – Join a team
- `POST /teams/:team_id/leave/:user_id/` – Leave a team

## Task

- `GET /tasks/:id/` – View a task
- `POST /tasks/add` – Create a task
- `POST /tasks/update/:id/` – Update a task (creator/collaborator/team member or superuser)
- `POST /tasks/delete/:id/` – Delete a task (creator or superuser)
- `POST /tasks/:id/add-sub-task` – Create and assign a subtask to a task
- `POST /tasks/:id/add-sub-team` – Create and assign a team to a task