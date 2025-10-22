# CineCritic 🎞️

## 📖 Overview

CineCritic is a RESTful backend built with Flask that helps you manage films, genres, user reviews, and personal watchlists. It features JWT authentication, role-based access control, data validation, and database migrations to keep your app secure and scalable. Whether you're building a movie discovery app or a review community, CineCritic provides a solid foundation to get started quickly.

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
- 🗄️ Alembic migrations with seed commands to demonstrate database versioning and sample data.

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

### 1. Clone the repository

```bash
git clone https://github.com/vetematts/CineCritic.git
```
This command downloads the project files to your local machine.

```bash
cd CineCritic
```
Change into the project directory to start working.

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
```
Creates a new virtual environment named `.venv` to isolate dependencies.

**Activate the virtual environment:**

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```
Installs all required Python packages specified in `requirements.txt`.

### 4. Configure environment variables

```bash
cp .env.default .env
```
Copies the example environment file to `.env` where you will set your configuration.

Edit `.env` with your preferred text editor and update the following keys:

```
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/<database_name>
JWT_SECRET_KEY=<your_secret_key>
```
Replace `<user>`, `<password>`, `<database_name>`, and `<your_secret_key>` with your actual database credentials and a secret key for JWT.

### 5. Install and set up PostgreSQL

If you don't have PostgreSQL installed, follow the instructions below.

<details>
<summary>🍏 macOS Installation</summary>

You can install PostgreSQL using Homebrew:

```bash
brew install postgresql
```
Start the PostgreSQL service:

```bash
brew services start postgresql
```

</details>

<details>
<summary>🐧 Linux / Windows WSL Installation</summary>

Install PostgreSQL using your package manager (example shown for Debian/Ubuntu):

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

Start the PostgreSQL service:

```bash
sudo service postgresql start
```

For other distributions, use the equivalent package commands (e.g., `dnf`, `pacman`).

</details>

### 6. Create the database and user

Connect to PostgreSQL and run the following commands to create your database and user:

```sql
CREATE DATABASE cinecritic_dev;
CREATE USER cinecritic WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE cinecritic_dev TO cinecritic;
```
This sets up a database named `cinecritic_dev` and a user `cinecritic` with password `password`.
⚠️ Adjust these as needed.

### 7. Apply database migrations

```bash
flask db upgrade
```
This command applies all Alembic migrations to set up your database schema.

If you need to reset migrations:

```bash
flask db downgrade && flask db upgrade
```
This will revert and re-apply migrations.

### 8. Seed demo data (optional)

```bash
flask ops create
flask ops seed
```
Creates tables and seeds the database with sample data for testing and development.

### 9. Run the API server

```bash
flask run
```
Starts the Flask development server. The API will be available at `http://127.0.0.1:5000/`.

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

<details>
<summary>Auth (`/auth`)</summary>

### Auth (`/auth`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create a new user account |
| POST | `/auth/login` | Authenticate and obtain JWT |
| GET | `/auth/me` | Current user profile (requires auth) |
| GET | `/auth/users` | List all users (admin only) |
| DELETE | `/auth/users/<id>` | Remove a user (admin only) |

</details>

<details>
<summary>Films (`/films`)</summary>

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

</details>

<details>
<summary>Genres (`/genres`)</summary>

### Genres (`/genres`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/genres` | List genres |
| POST | `/genres` | Create genre (admin only) |
| DELETE | `/genres/<id>` | Delete genre (admin only) |

</details>

<details>
<summary>Reviews (`/films/&lt;int:film_id&gt;/reviews`)</summary>

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

</details>

<details>
<summary>Watchlist (`/users/me/watchlist`)</summary>

### Watchlist (`/users/me/watchlist`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/me/watchlist` | List current user's watchlist entries |
| POST | `/users/me/watchlist` | Add film to watchlist |
| DELETE | `/users/me/watchlist/<film_id>` | Remove film from watchlist |

</details>

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
