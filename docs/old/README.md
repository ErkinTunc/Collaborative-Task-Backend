# Application Web de Gestion de Tâches

> **Développeurs** : Erkin Tunc BOYA, Mohamed SAIDANE 
> **Technologies** : Python Django, Bootstrap

---

## Description

C'est une application web multi-utilisateur permettant la gestion de tâches.  
L'application est construite avec Django et utilise Bootstrap pour le style.

---

## Comment démarrer

1. **Cloner le projet**
```bash
git clone <repo-url>
cd App-Web-Gestion-De-taches
```

2. **Créer un environnement virtuel**  
Chaque ordinateur doit avoir son propre environnement virtuel (non partagé via Git).
```bash
python -m venv tp-env
```

3. **Activer l’environnement virtuel**
```bash
# UNIX
source tp-env/bin/activate
# Windows
tp-env\Scripts\activate
```

4. **Installer les dépendances**
```bash
# Installer Django
python -m pip install Django
# Installer les dépendances (pour la gestion d’images)
pip install Pillow 
```

5. **Lancer le serveur**
```bash
python manage.py runserver
```

---

## Fonctionnalités

- **Authentification** : chaque utilisateur doit se connecter ou s’inscrire pour accéder au site. S'ils essaient, ils seront redirigés vers la page de connexion.

### Fonctionnalités des Tâches

- Une tâche comporte un titre, un statut, une description, une liste de sous-tâches, une liste de personnes et une liste d'équipes associées.
- Une tâche peut être privée (visible uniquement par les personnes/équipes associées) ou publique.
- L'utilisateur peut créer (seules les personnes travaillant sur cette tâche et le créateur peuvent), modifier et (seul le créateur d'une tâche peut) supprimer une tâche.
- Lorsqu'une tâche est supprimée, tous ses liens avec les équipes et les personnes sont automatiquement supprimés.

### Fonctionnalités des Équipes

- Une équipe a un nom et une liste de personnes.
- Un utilisateur peut créer, entrer, quitter (s'il est dans l'équipe), modifier et supprimer une équipe.
- Lorsqu'une équipe est supprimée, tous ses liens avec les tâches et les personnes sont automatiquement supprimés.

### Fonctionnalités des Utilisateurs

- Un utilisateur a un nom, un e-mail, une description, un mot de passe et une image.
- Un utilisateur peut consulter le profil d’un autre utilisateur/équipe, ainsi que les tâches publiques qui lui sont attribuées.
- Un utilisateur peut modifier et supprimer son profil (ainsi que le super utilisateur).
- Un super user peut créer un utilisateur
- Lorsqu’un utilisateur est supprimé, toutes ses relations avec les tâches et les équipes sont automatiquement supprimées.

---

## Structure de projet

```bash
├── README.md
├── db.sqlite3
├── manage.py
├── pictures
│     └── profile_pictures
│     └── favicon
├── task_manager # la coeur d'application
├── tasks # App contenant tous les modèles de User,Team et Task
├── tp-env # l’environnement virtuel
└── users # App utilisée pour l'authentification
```

---

## Routes API

### Page d’accueil
- `GET /` – Affiche toutes les tâches public et les tache d'utilisateur
- `GET /control-panel/` - C'est le panel de control pour le superuser. Cela affiche tous le taches,equipes et utilisateur.

### Authentification
- `POST /register` – Créer un compte
- `POST /login` – Se connecter
- `POST /logout` – Se déconnecter

### Utilisateur
- `GET /users/:id` – Voir le profil d’un utilisateur, ses tâches et ses équipes
- `POST /users/add/` – Créer un utilisateur
- `POST /users/update/:id` – Mettre à jour le profil
- `POST /users/delete/:id` – Supprimer un utilisateur

### Équipe
- `GET /teams/:id` – Voir le profil d’une équipe
- `POST /teams/add` – Créer une équipe
- `POST /teams/update/:id` – Mettre à jour une équipe
- `POST /teams/delete/:id` – Supprimer une équipe
- `POST /teams/:id/enter/:user-id` – Rejoindre une équipe
- `POST /teams/:id/leave/:user-id` – Quitter une équipe

### Tâche
- `GET /tasks/:id` – Voir une tâche
- `POST /tasks/add` – Créer une tâche
- `POST /tasks/update/:id` – Mettre à jour une tâche
- `POST /tasks/delete/:id` – Supprimer une tâche
- `POST tasks/:id/add-sub-task` – Créer et Assigner une sous-tache
- `POST tasks/:id/add-sub-team` – Créer et Assigner une équipe

---

## Modèles (Entities)

### Task
```bash
{
  "private": boolean,
  "creator": User,

  "title": string,
  "status": "todo" || "in_progress" || "done",
  "description": string,

  "users": [User],    // Le list de Users qui travailent sur cela
  "teams": [Team],    // Le list de Teams 
  "subtasks": [Task], // Le sub-tasks de cette Task

  "created_at": Date,
  "updated_at": Date, 
  "deadline": Date
}
```

### Team
```bash
{
  "name": string,
  "users": [User]
}
```

### User
Classe utilisateur par défaut :
```bash
{
  "id": int,
  "name": string,
  "email": string,
  "password": string
}
```

### UserProfile
```bash
{
  "user": User, // Relation un-à-un
  "description": string,
  "image": *.png // généralement au format .png ou autre | Dossier "pictures"
}
```
