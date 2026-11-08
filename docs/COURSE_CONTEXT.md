# Course Context

TeamForge started as a Django collaborative task manager for **Web Serveur – L2** at ISIMA, as recorded in the project's earlier documentation. It has since been developed further as a backend portfolio project.

The original assignment handout is not included in this repository. The outline below reflects the project's existing course notes, **not an independently verified copy of the marking rubric**.

## Original scope

The exercise covered the main parts of a collaborative application:

- Registration and login
- Users and profiles
- Creating, editing and deleting tasks
- Public and private tasks
- Teams and membership changes
- Assigning tasks to users and teams
- Linking subtasks to larger tasks
- Django views and templates

Those features provide a useful starting point because they introduce several kinds of users interacting with the same data.

## What we focused on afterward

The most interesting problem was not displaying a task list. It was deciding what each user should be allowed to do.

For instance, a collaborator can edit an assigned task but cannot delete it. A user can see a private task through membership in an assigned team. And an outsider should not be able to add themselves to a team by sending a crafted POST request.

The repository now makes these decisions explicit:

- Shared visibility/edit helpers in `tasks/permissions.py`
- Permission checks at the view level
- Form restrictions for assigning teams to tasks
- A written [permission model](PERMISSIONS.md)
- **21 automated Django tests** in `tasks/tests.py`, mainly covering authorization
- Example data and screenshots to make the application easier to explore

These are features of the **current repository**, not a claim that the original course required or did not require each one.

## Why this remains a student project

The application uses Django templates and SQLite, with no separate frontend or REST API. That choice kept development manageable and made it easier to concentrate on relational modeling and access rules.

It is not a production-hardened collaboration platform. In particular, the trust model gives all team members equal membership-management rights, tests cover only part of the application, and deployment/security checks still need work. These are described in [Security](SECURITY.md) and [Testing](TESTING.md).

For a backend internship, the useful part of this project is the ability to explain the decisions, inspect their implementation and run tests—not the claim that it is a commercial product.
