# Testing

TeamForge currently defines **21 automated Django tests** in `tasks/tests.py`. They are written with `django.test.TestCase` and focus on authorization: users should not gain access simply by changing a submitted ID or URL.

This is not full application coverage. The list below distinguishes what is already tested from what is still worth testing.

## Run the tests

Install dependencies and set a local `DJANGO_SECRET_KEY` as described in the [README](../README.md). Then run:

```bash
python manage.py test tasks -v 2
```

Django creates and destroys a separate test database. The tests do not need the seeded demo accounts.

For a basic configuration check:

```bash
python manage.py check
```

## What is covered now

| Test class | Count | Scenarios |
| --- | ---: | --- |
| `TaskTeamAuthorizationTests` | 3 | Reject foreign-team assignments on create/update; preserve existing team links on edit |
| `TaskDeletionPermissionTests` | 5 | Outsiders and collaborators cannot delete; private task is hidden from outsider on delete route; creator deletes via POST; missing task returns 404 |
| `TeamUpdatePermissionTests` | 3 | Outsider blocked; member allowed; missing team returns 404 |
| `TeamDeletionPermissionTests` | 4 | Outsider blocked; member can delete only via POST; superuser allowed; missing team returns 404 |
| `TeamMembershipPermissionTests` | 6 | Outsiders cannot join/remove members; members can add/remove; self-leave works; GET cannot change membership; missing target profile returns 404 |
| **Total** | **21** | |

These tests use Django's test client and test users, including creators, assigned users, team members, outsiders and superusers as applicable.

A particularly useful example is the team-assignment form test: an outsider cannot submit the ID of an unrelated team to attach it to their task. The corresponding update test also checks that a pre-existing team link survives editing.

## What is not yet covered well

The following should be treated as **future test cases**, not existing automated coverage:

- A complete visibility matrix for public/private tasks on dashboards, detail pages, profiles, team pages and linked subtasks.
- Task update permissions for each role (creator, assignee, team member, outsider, superuser), including both GET and POST.
- Subtask creation and its permission checks, including cycles and multiple-parent edge cases.
- Profile update/deletion permissions, missing-profile behavior and image upload validation.
- Registration, login, logout and CSRF rejection cases.
- Deletion side effects: creator removal cascading to their tasks, and cleanup of team/task relations.
- Upload handling, deployment configuration and any concurrency/performance claims.

The existing permission helpers provide a good starting point for these tests; see [Permissions](PERMISSIONS.md).

## Practical manual checks

For a quick demonstration, sign in as two different normal users and compare which private tasks they can see. Confirm that a collaborator can open the edit form but not delete someone else's task. Try changing team membership as a member and as an outsider. Verify a superuser can access the control panel.

These manual checks are useful for UI behavior, but should not be reported as automated test coverage.

## Scope and next step

The current suite gives concrete evidence for several permission boundaries, not a guarantee that every security issue has been found. The next useful improvement is a test matrix for task visibility and edit rights; it is more valuable here than introducing a new testing framework.
