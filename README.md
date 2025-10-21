# CineCritic 🎞️

<details>
<summary>📖 Overview</summary>

CineCritic is a RESTful backend built with Flask that helps you manage films, genres, user reviews, and personal watchlists. It features JWT authentication, role-based access control, data validation, and database migrations to keep your app secure and scalable. Whether you're building a movie discovery app or a review community, CineCritic provides a solid foundation to get started quickly.

</details>

---

## 🎯 Target Users

- 🎬 **Media product teams:** Power your movie discovery apps with a reliable backend.
- 🧑‍💻 **Developers & students:** Explore a full-featured Flask stack with authentication, migrations, seed data.
- 👩‍🏫 **Educators:** Demonstrate best practices for REST APIs, schema validation, and role-based access control.

*CineCritic provides the API surface for building review communities without reinventing core plumbing.*

---

## 📑 Table of Contents
- [📖 Overview](#-overview)
- [🎯 Target Users](#-target-users)
- [✨ Features](#-features)
- [⚙️ Requirements](#-requirements)
- [🚀 Quick Setup](#-quick-setup)
- [🔒 Security & Data Considerations](#-security--data-considerations)
- [📡 API Reference](#-api-reference)

## ✨ Features

- 🍿 RESTful resources for films, genres, reviews, and watchlists with robust validation.
- 🧭 Clear separation of concerns: controllers, models, schemas, and utilities.
- 🛡️ Role-aware JWT authentication supporting admin and standard users.
- 🗄️ Production-ready Alembic migrations and seed commands for demo data.

---

## ⚙️ Requirements

<details>
<summary>System Requirements</summary>

- **Python:** 3.10 or newer
- **pip:** Python package manager
- **PostgreSQL:** 13+ (local or remote instance)
- **Flask CLI:** installed automatically via `requirements.txt`

Check your versions:

```bash
python3 --version
pip3 --version
```

</details>

| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 3.1.x | Web application framework |
| Flask-SQLAlchemy | 3.1.x | ORM integration |
| Flask-Migrate | 4.1.x | Alembic migrations |
| Flask-JWT-Extended | 4.7.x | JWT authentication |
| Marshmallow | 4.0.x | Validation & serialization |
| psycopg2-binary | 2.9.x | PostgreSQL driver |

---

## 🚀 Quick Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-org/CineCritic.git
   cd CineCritic
   ```

2. **Create and activate a virtual environment**

   ```bash
   python3 -m venv .venv
   # macOS/Linux
   source .venv/bin/activate
   # Windows CMD
   .venv\Scripts\activate
   # Windows PowerShell
   .venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Copy `.env.default` to `.env` and update the values:

   ```bash
   cp .env.default .env
   ```

   Required keys:

   ```
   DATABASE_URL=postgresql://<user>:<password>@localhost:5432/<database_name>
   JWT_SECRET_KEY=<your_secret_key>
   ```

5. **Set up the database**

   Create your PostgreSQL database and user (example):

   ```sql
   CREATE DATABASE cinecritic_dev;
   CREATE USER cinecritic WITH PASSWORD 'password';
   GRANT ALL PRIVILEGES ON DATABASE cinecritic_dev TO cinecritic;
   ```

   Then apply migrations:

   ```bash
   flask db upgrade
   ```

    If you need to reset migrations:
    ```bash
    flask db downgrade && flask db upgrade
    ```

   Optionally seed demo data:

   ```bash
   flask ops seed
   ```

6. **Run the API**

   ```bash
   flask run
   ```

   The server will be available at `http://127.0.0.1:5000/`.

---

## 🔒 Security & Data Considerations

- Role-based JWT authentication protects admin and user endpoints.
- Tokens expire according to Flask-JWT-Extended defaults for security.
- Sensitive configuration values like database credentials and JWT secrets are stored in `.env` (not committed to version control).
- Centralized error handling ensures consistent JSON responses for API consumers.

---

## 📡 API Reference

Base URL: `http://127.0.0.1:5000/`
All responses are JSON. Pagination parameters: `?page=` and `?per_page=` where applicable.

### Auth (`/auth`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create a new user account |
| POST | `/auth/login` | Authenticate and obtain JWT |
| GET | `/auth/me` | Current user profile (requires auth) |
| GET | `/auth/users` | List all users (admin only) |
| DELETE | `/auth/users/<id>` | Remove a user (admin only) |

### Films (`/films`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/films` | List films (filters: title, year, director, genre_id) |
| GET | `/films/<id>` | Retrieve a single film |
| POST | `/films` | Create a film (admin only) |
| PATCH | `/films/<id>` | Update film fields (admin only) |
| DELETE | `/films/<id>` | Delete a film (admin only) |
| GET | `/films/<id>/genres` | List genres linked to a film |
| POST | `/films/<id>/genres/<genre_id>` | Attach genre (admin only) |
| DELETE | `/films/<id>/genres/<genre_id>` | Detach genre (admin only) |

### Genres (`/genres`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/genres` | List genres |
| POST | `/genres` | Create genre (admin only) |
| DELETE | `/genres/<id>` | Delete genre (admin only) |

### Reviews (`/films/<int:film_id>/reviews`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/films/<film_id>/reviews` | List published reviews for a film |
| POST | `/films/<film_id>/reviews` | Create review for current user |
| GET | `/films/<film_id>/reviews/<id>` | View review (published or owner/admin) |
| PATCH | `/films/<film_id>/reviews/<id>` | Update review (owner/admin) |
| DELETE | `/films/<film_id>/reviews/<id>` | Delete review (owner/admin) |
| POST | `/films/<film_id>/reviews/<id>/publish` | Publish review (owner/admin) |
| POST | `/films/<film_id>/reviews/<id>/flag` | Flag review (any authenticated user) |

### Watchlist (`/users/me/watchlist`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/me/watchlist` | List current user's watchlist entries |
| POST | `/users/me/watchlist` | Add film to watchlist |
| DELETE | `/users/me/watchlist/<film_id>` | Remove film from watchlist |

### Common Response Codes

- `200 OK` – Successful request
- `201 Created` – Resource created
- `204 No Content` – Resource deleted
- `400 Bad Request` – Validation or format error
- `401 Unauthorised` – Missing or invalid JWT
- `403 Forbidden` – Role or ownership violation
- `404 Not Found` – Resource unavailable
- `409 Conflict` – Duplicate or constraint violation
- `500 Server Error` – Unexpected failure

This project is for educational purposes only and not intended for production use.
