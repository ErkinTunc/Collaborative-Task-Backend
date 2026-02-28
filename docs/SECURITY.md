# Security

This project relies on Django’s built-in authentication system and implements explicit object-level authorization inside views.

The security model focuses on controlling access to data and preventing unauthorized modifications.

---

## 1. Authentication Enforcement

- All core views are protected using `@login_required`.
- Anonymous users are redirected to the login page.
- Access to tasks, teams, and profiles requires authentication.

This ensures the system is not publicly accessible.

---

## 2. Object-Level Authorization

Authorization logic is implemented directly inside views.

Access and modification rules are explicitly checked before performing actions.

Examples:

- Only superusers can access `/control-panel/`
- Only the task creator (or superuser) can delete a task
- Only team members (or superuser) can update/delete a team
- Only the profile owner (or superuser) can update/delete a profile
- Task updates require one of:
  - Creator
  - Assigned user
  - Member of assigned team
  - Superuser

If a user does not meet the required conditions, the request is rejected.

This prevents horizontal privilege escalation.

---

## 3. CSRF Protection

All form-based POST requests use Django’s CSRF protection.

Sensitive actions such as:

- Logout
- Delete
- Update
- Create

are performed using POST requests protected by CSRF tokens.

---

## 4. Password Handling

- User passwords are handled by Django’s built-in authentication system.
- Passwords are hashed automatically.
- Password validation rules are enabled in Django settings.

No passwords are stored or handled manually.

---

## 5. Superuser Override

Superusers bypass object-level restrictions.

This enables administrative control without modifying domain rules.

---

## Summary

Security in this project is primarily enforced through:

- Mandatory authentication
- Explicit object-level authorization checks
- CSRF-protected POST operations
- Django’s built-in password hashing system

The focus is on correct permission enforcement rather than production hardening.