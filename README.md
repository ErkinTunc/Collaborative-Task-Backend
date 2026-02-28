# Collaborative Task Backend

**Multi-User Collaborative Backend (Django)**

A backend-oriented system exploring object-level authorization, relational modeling, and multi-user domain design.

This project focuses on reasoning about _who can see, modify, and delete what_ in a collaborative environment.

---

## System Motivation

Many collaborative systems appear simple at the interface level but become complex when enforcing:

- Visibility rules
- Ownership semantics
- Multi-entity assignment
- Hierarchical relationships
- Consistent permission enforcement

This project models those challenges explicitly.

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.x |
| Framework | Django 5.x |
| Database | SQLite (dev) / PostgreSQL (prod-ready) |
| UI | Bootstrap (server-rendered templates) |


---

## Core Technical Challenges

- Designing object-level visibility rules across:
  - Public tasks
  - Direct user assignments
  - Team-based propagation
- Modeling directed subtask graphs using self-referencing relations
- Separating authentication from business logic
- Enforcing permissions without hidden abstractions
- Maintaining relational integrity via lifecycle signals

The emphasis is correctness and reasoning — not UI complexity.

---

## Architectural Decisions

App Separation:

```bash
users/ → Authentication & profile domain
tasks/ → Business domain (Task, Team, permission logic)
```

Key decisions:

- View-level authorization (explicit request boundary control)
- Directed self-referencing ManyToMany for task hierarchies
- Explicit creator vs collaborator distinction
- Minimal use of signals (only lifecycle consistency)
- Server-rendered design (no DRF abstraction layer)

Trade-offs are documented in [ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## Engineering Focus

This project demonstrates:

- Domain modeling with complex associations
- Object-level access control
- Directed graph modeling in relational databases
- Explicit trade-off reasoning
- Awareness of production concerns (security, scaling, testing)

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Data Model](docs/DATA_MODEL.md)
- [Permission Model](docs/PERMISSIONS.md)
- [Security Review](docs/SECURITY.md)
- [Testing Strategy](docs/TESTING.md)
- [Course Context](docs/COURSE_CONTEXT.md)

---

## Running the Project Locally

1. **Clone the project**

```bash
git clone <repo-url>
cd App-Web-Gestion-De-taches
```

1. **Create a virtual environment**  
   Each computer must have its own virtual environment (not shared via Git).

```bash
Remove-Item -Recurse -Force .\venv
python -m venv venv
```

3. **Activate the virtual environment**

```bash
# UNIX
source venv/bin/activate

# Windows (PowerShell)
.\venv\bin\Activate.ps1
```

4. **Install dependencies**

```bash
# Install Django
python -m pip install Django

# Install dependencies (for image handling)
pip install Pillow
```

5. **Run the server**

```bash
python manage.py runserver
```

---

## Authors

- [Erkin Tunc BOYA](https://github.com/ErkinTunc)
- [Mohamed SAIDANE](https://github.com/Tounes-3220)

