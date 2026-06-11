# Hair Stylist Booking System

A backend API for managing hair stylist appointments. Clients can book,
view, and cancel appointments. The stylist manages availability and
views the full schedule.

## Tech Stack

- **Python 3.11** + **Flask** — web framework
- **SQLAlchemy** + **Alembic** — ORM and migrations
- **PostgreSQL** (Supabase) — database
- **Flask-JWT-Extended** — authentication
- **pytest** — testing
- **Render** — deployment

## Features

- Client registration and JWT authentication
- Role-based access control (stylist vs client)
- Appointment booking with conflict detection
- Stylist availability management
- Middleware-based request logging and error handling
- Full test suite (unit + integration)

## Prerequisites

- Python 3.11+
- pip
- Git
- A PostgreSQL database (free tier at [supabase.com](https://supabase.com))

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

| Variable         | Description                                          | Where to get it                                                          |
| ---------------- | ---------------------------------------------------- | ------------------------------------------------------------------------ |
| `DATABASE_URL`   | PostgreSQL connection string                         | Supabase dashboard → Settings → Database → URI                           |
| `JWT_SECRET_KEY` | Long random string for signing JWT tokens            | Generate with `python -c "import secrets; print(secrets.token_hex(32))"` |
| `FLASK_ENV`      | Set to `development` locally, `production` on server | Set manually                                                             |

## Local Setup

1. Clone the repository:

git clone https://github.com/codegorl23/Hair-Booking-System.git

cd Hair-Boooking-System

2. Create and activate a virtual environment:
   python -m venv
   source venv/bin/activate #Windows:venvScriptsactivate

3. Install dependencies:
   pip intall -r requirements.txt

4. Create a PostgreSQL database (Supabase free tier recommended).

5. Copy `.env.example` to `.env` and fill in your values:
   cp.env.example.env

6. Run database migrations:
   flask db upgrade

7. Seed the database with sample data:
   python seed.py

## Running the Application

python run.py

The API will be available at `http://127.0.0.1:5000`.
Verify it's running: `curl http://127.0.0.1:5000/health`

## Running the Tests

pytest -v

All tests run against an in-memory SQLite database. No external dependencies required.

## API Reference

| Method | Endpoint             | Description               | Auth             |
| ------ | -------------------- | ------------------------- | ---------------- |
| GET    | `/health`            | Health check              | None             |
| GET    | `/services`          | List all active services  | None             |
| POST   | `/auth/register`     | Register a new user       | None             |
| POST   | `/auth/login`        | Login and receive JWT     | None             |
| POST   | `/clients`           | Register a new client     | None             |
| GET    | `/clients`           | List all clients          | Stylist          |
| POST   | `/appointments`      | Book an appointment       | Client           |
| GET    | `/appointments`      | List all appointments     | Stylist          |
| GET    | `/appointments/<id>` | Get a single appointment  | Stylist or owner |
| PATCH  | `/appointments/<id>` | Update appointment status | Stylist or owner |

## Architecture Decisions

**Service layer separation:** Business logic (conflict checking, role validation) lives in
`app/services/`, not in route handlers. This keeps routes thin and makes the business logic
testable without HTTP.

**JWT authentication:** Stateless tokens are used instead of server-side sessions.
This means the server holds no session state — any server instance can verify any token,
making the system easier to scale horizontally.

**PostgreSQL on Supabase:** SQLite was used during development for simplicity.
PostgreSQL is used in production for concurrent write support and strict type enforcement.
Supabase provides managed PostgreSQL with no infrastructure to maintain.

## Live Demo

[https://hair-booking-system.onrender.com](https://hair-booking-system.onrender.com)
