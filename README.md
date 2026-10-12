# KanMind Backend

REST API for **KanMind**, a Kanban board application. Users can register, create boards,
invite members, manage tasks with status and priority, assign assignees and reviewers,
and discuss tasks in comments.

The backend is built with Django and Django REST Framework. The matching frontend
(Vanilla JavaScript) is **not** part of this repository.

---

## Tech Stack

| Component | Version |
|---|---|
| Python | 3.12 or newer |
| Django | 6.1 |
| Django REST Framework | 3.18 |
| django-cors-headers | 4.9 |
| python-dotenv | 1.2 |
| Database | SQLite (created automatically) |

---

## Installation

The commands below are shown for **Windows (PowerShell)** and **macOS / Linux**.
Where they differ, both variants are listed.

### 1. Clone the repository

```bash
git clone https://github.com/SchumacherKevin/kanmind_backend.git
cd kanmind_backend
```

### 2. Create and activate a virtual environment

**Windows (PowerShell)**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

When the environment is active, your terminal prompt starts with `(.venv)`.

### 3. Install the dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the environment file with your secret key

Django needs a secret key. It is **not** stored in the repository and has to be
created locally.

Copy the template:

**Windows (PowerShell)**

```powershell
Copy-Item core\.env.template core\.env
```

**macOS / Linux**

```bash
cp core/.env.template core/.env
```

Generate a new key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Open `core/.env` and replace the placeholder with the generated key:

```env
SECRET_KEY = 'paste-your-generated-key-here'
```

> `core/.env` is listed in `.gitignore` and must never be committed.

### 5. Create the database

```bash
python manage.py migrate
```

This creates the SQLite file `db.sqlite3` in the project root. The database is
also excluded from Git.

### 6. Create an admin user (optional)

```bash
python manage.py createsuperuser
```

The admin panel is available at `http://127.0.0.1:8000/admin/` and lists all
boards, tasks and comments.

> Note: Users log in to the API with their **email address**. A superuser created
> with a username that is not an email address can use the admin panel, but not
> the frontend login.

### 7. Start the development server

```bash
python manage.py runserver
```

The API is now available at **`http://127.0.0.1:8000/api/`**.

---

## Connecting the Frontend

1. Get the KanMind frontend and open it in Visual Studio Code.
2. Check `shared/js/config.js`: `API_BASE_URL` must be `http://127.0.0.1:8000/api/`.
3. Start the frontend with the **Live Server** extension (right click `index.html`
   and choose *Open with Live Server*).

The backend only accepts browser requests from these addresses
(`CORS_ALLOWED_ORIGINS` in `core/settings.py`):

- `http://127.0.0.1:5500`
- `http://localhost:5500`

If Live Server runs on a different port, add that address to
`CORS_ALLOWED_ORIGINS`.

**Guest login:** the frontend's guest login button uses the credentials stored in
`GUEST_LOGIN` in `shared/js/config.js`. Register a user with exactly this email
address and password once (via the frontend or `POST /api/registration/`), then
the button works.

---

## Authentication

The API uses **token authentication**. Registration and login return a token.
Every other request must send it in the `Authorization` header:

```
Authorization: Token <your-token>
```

Requests without a valid token receive `401 Unauthorized`.

---

## API Endpoints

All endpoints start with `/api/`.

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `registration/` | Create a user (`fullname`, `email`, `password`, `repeated_password`) and return a token |
| POST | `login/` | Log in with `email` and `password` and return a token |
| GET | `email-check/?email=<email>` | Return the user with this email address, or `404` |

### Boards

| Method | Endpoint | Description |
|---|---|---|
| GET | `boards/` | List all boards the user owns or is a member of |
| POST | `boards/` | Create a board (`title`, `members`); the user becomes the owner |
| GET | `boards/{board_id}/` | Board details with members and tasks |
| PATCH | `boards/{board_id}/` | Update the title and/or the member list |
| DELETE | `boards/{board_id}/` | Delete the board including all tasks and comments |

### Tasks

| Method | Endpoint | Description |
|---|---|---|
| POST | `tasks/` | Create a task on a board |
| GET | `tasks/assigned-to-me/` | Tasks where the user is the assignee |
| GET | `tasks/reviewing/` | Tasks where the user is the reviewer |
| PATCH | `tasks/{task_id}/` | Update a task |
| DELETE | `tasks/{task_id}/` | Delete a task |

Allowed values:

- `status`: `to-do`, `in-progress`, `review`, `done`
- `priority`: `low`, `medium`, `high`

### Comments

| Method | Endpoint | Description |
|---|---|---|
| GET | `tasks/{task_id}/comments/` | List the comments of a task, oldest first |
| POST | `tasks/{task_id}/comments/` | Add a comment (`content`) |
| DELETE | `tasks/{task_id}/comments/{comment_id}/` | Delete a comment |

---

## Permissions

| Action | Allowed for |
|---|---|
| View / update a board | Board owner and members |
| Delete a board | Board owner only |
| Create / update a task, read / write comments | Board owner and members of the task's board |
| Delete a task | Task creator or board owner |
| Delete a comment | Comment author only |

Unauthorized actions return `403 Forbidden`; resources that do not exist return
`404 Not Found`.

---

## Project Specifics

- **Email as username:** on registration the email address is stored as Django's
  `username`, so users log in with email and password.
- **Full name:** `fullname` is split into `first_name` (first word) and `last_name`
  (rest) and joined again in every response.
- **Assignee and reviewer** must be the owner or a member of the task's board,
  otherwise the request returns `400`.
- **The board of a task cannot be changed.** A `PATCH` may still send the current
  board ID (the frontend does), but a different board returns `400`.
- **Optimized queries:** counters such as `member_count`, `ticket_count` and
  `comments_count` are calculated in the database with `annotate()`, and related
  users are loaded with `select_related()` / `prefetch_related()` to avoid N+1
  queries.

---

## Project Structure

```
kanmind_backend/
├── core/                 # Project settings and main URL configuration
│   ├── settings.py
│   ├── urls.py
│   └── .env.template     # Template for the local secret key
├── auth_app/             # Registration, login and email check
│   └── api/
│       ├── serializers.py
│       ├── urls.py
│       └── views.py
├── kanban_app/           # Boards, tasks and comments
│   ├── models.py
│   ├── admin.py
│   └── api/
│       ├── permissions.py
│       ├── serializers.py
│       ├── urls.py
│       └── views.py
├── manage.py
└── requirements.txt
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `Activate.ps1 cannot be loaded because running scripts is disabled` (Windows) | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once in PowerShell, then activate again. |
| `The SECRET_KEY setting must not be empty` | `core/.env` is missing or still contains no key, see step 4. |
| Frontend shows network or CORS errors | Make sure the server is running and the Live Server address is listed in `CORS_ALLOWED_ORIGINS`. |
| `no such table` errors | Run `python manage.py migrate`. |
