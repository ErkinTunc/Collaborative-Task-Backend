# Course Context

This project originated as an academic assignment for the course  
**“Web Serveur – L2”** (ISIMA).

The assignment required implementing a collaborative task management system using Django.

---

## Original Specification Summary

The core requirements included:

- Multi-user authentication (registration and login)
- Task creation, modification, deletion
- Public and private task visibility
- Team creation and membership
- Task assignment to users and teams
- Subtask relationships
- Profile visualization

The emphasis of the assignment was functional correctness.

---

## What Was Required

From the official specification:

- Tasks with title, status, description
- Subtasks
- Assignment to users and teams
- Public vs private visibility
- Team join/leave functionality
- Basic routing and views
- Django-based MVC structure

The evaluation criteria focused on:

- Functionality
- User interface
- Code quality
- Documentation
- Respect of requirements

---

## What Was Extended Beyond Requirements

This repository goes beyond the minimum academic requirements by:

1. Explicitly separating authentication and business domains
2. Formalizing object-level authorization rules
3. Modeling directed subtask relationships
4. Implementing lifecycle cleanup using Django signals
5. Documenting architectural trade-offs
6. Documenting security limitations
7. Documenting future extension paths
8. Structuring documentation into modular `/docs/` sections

The goal shifted from:

> “Deliver a working assignment”

to:

> “Design a system with explicit architectural reasoning.”

---

## Design Intent

While the assignment required a working application, this version treats the project as a backend architecture exercise:

- Focus on permission logic correctness
- Clear separation of concerns
- Explicit trade-offs (no service layer, no DRF)
- Transparent authorization flow
- Awareness of scalability and security limitations

---

## Limitations

This project remains:

- Server-rendered (not API-first)
- Not production-hardened
- Not performance-optimized
- Without full automated test coverage

These limitations are acknowledged and documented in the respective sections.

---

## Educational Value

This project demonstrates:

- Understanding of relational modeling
- Multi-actor permission systems
- Architectural constraint reasoning
- System evolution awareness

It reflects an academic exercise intentionally extended toward backend engineering practice.