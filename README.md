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
- [API Specification](docs/API.md)
- [Data Model](docs/DATA_MODEL.md)
- [Permission Model](docs/PERMISSIONS.md)
- [Security Review](docs/SECURITY.md)
- [Testing Strategy](docs/TESTING.md)
- [Course Context](docs/COURSE_CONTEXT.md)

---

## Running the Project Locally

1. **Clone the project**

```bash
git clone https://github.com/ErkinTunc/Collaborative-Task-Backend.git
cd Collaborative-Task-Backend
```

2. **Create a virtual environment**

Each computer must have its own virtual environment (not shared via Git).

```bash
python -m venv venv
```

3. **Activate the virtual environment**

```bash
# UNIX
source venv/bin/activate

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
```

4. **Install dependencies**

```bash
pip install -r requirements.txt
```

5. **Configure SECRET_KEY**

Generate a local secret key (do not commit it to GitHub).

```powershell
# Windows (PowerShell)
$env:DJANGO_SECRET_KEY = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

```bash
# UNIX
export DJANGO_SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
```

6. **Initialize the database**

```bash
python manage.py migrate
python manage.py createsuperuser
```

7. **Run the server**

```bash
python manage.py collectstatic --noinput
python manage.py runserver
```

Open http://127.0.0.1:8000/



---

## Authors

- [Erkin Tunc BOYA](https://github.com/ErkinTunc)
- [Mohamed SAIDANE](https://github.com/Tounes-3220)


