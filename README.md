CineCritic API

Overview

CineCritic is a RESTful API for tracking films, reviews, genres, and user watchlists.
It uses Flask with SQLAlchemy ORM, Marshmallow for validation/serialization, JWT for authentication, and Alembic for database migrations.

Packages used:
	•	Flask
	•	SQLAlchemy
	•	Marshmallow
	•	Flask-JWT-Extended
	•	psycopg2
	•	python-dotenv
	•	Flask-Migrate

Requirements
	•	Python 3
	•	Works on MacOS or Windows

Installation

1. Create a virtual environment

python3 -m venv venv

2. Activate the virtual environment

source venv/bin/activate   # MacOS/Linux
venv\Scripts\activate      # Windows

3. Install dependencies

pip install -r requirements.txt

Database Setup

1. Initialize Alembic migrations

flask db init

2. Create migration file

flask db migrate -m "initial schema"

3. Apply migrations

flask db upgrade

4. Seed data (optional)

flask ops seed

5. Drop and recreate (dev only)

flask ops drop
flask ops create

Running the API

Start the development server:

flask run

