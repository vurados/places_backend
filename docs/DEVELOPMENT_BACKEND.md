# Backend Development Guide

This guide is for developers focusing primarily on the application code, schemas, and API logic. It uses a containerized environment for high-frequency iteration without needing a full infrastructure VM.

## Prerequisites

- **Docker & Docker Compose**
- **Git**
- **Python 3.12** (local setup for IDE support, optional but recommended)

## Quick Start

### 1. Set Up Environment

```bash
cp .env.example .env
```

Ensure `DB_HOST=postgres` in your `.env` (since it will run inside Docker).

### 2. Start Services

```bash
docker compose -f docker-compose.dev.yml up --build
```

This will:

- Spin up **PostgreSQL**, **Redis**, and **MinIO**.
- Build and start the **App** container.
- Mount your local directory to `/app` inside the container.
- Start **Uvicorn** with `--reload` for instant changes.

### 3. Run Migrations

Migrations run automatically on container start. To run manually:

```bash
docker compose -f docker-compose.dev.yml exec app alembic upgrade head
```

## Workflow

### Instant Code Changes

Because the project root is mounted into the container, any change you save to a Python file will trigger a Uvicorn reload. You can view logs in real-time:

```bash
docker compose -f docker-compose.dev.yml logs -f app
```

### Accessing Databases

- **PostgreSQL**: `localhost:5432`
- **Redis**: `localhost:6379`
- **MinIO Console**: `http://localhost:9001` (user/pass from `.env`)

## Interactive Documentation

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Running Tests

### Full Test Suite

```bash
# Using Docker Compose
docker compose -f docker-compose.test.yml up --build
```

### Run Specific Tests

```bash
# Single file
docker compose -f docker-compose.dev.yml exec app pytest tests/test_auth.py -v

# With coverage
docker compose -f docker-compose.dev.yml exec app pytest --cov=app --cov-report=html
```

---

## Code Style

### Essential Tools

- **Black**: Code formatting (`black app/`)
- **isort**: Import sorting (`isort app/`)
- **flake8**: Linting (`flake8 app/`)

### Pre-commit Hooks

It's recommended to install pre-commit locally:

```bash
pip install pre-commit
pre-commit install
```

---

## Performance Tips

### Database Indexing

Add indexes for frequently queried fields in your models to avoid sequential scans.

### Async Operations

Always use `async/await` for database and network I/O. Avoid blocking calls like `time.sleep()` or synchronous requests.

### Caching

Use the integrated Redis instance for expensive query results or session data.

---

## Troubleshooting

### Database Connection

If the app can't connect to `postgres`, ensure your `.env` has `DB_HOST=postgres` (when running in Docker) or `DB_HOST=localhost` (when running locally).

### Resetting Development DB

To wipe the database and start fresh:

```bash
docker compose -f docker-compose.dev.yml down -v
docker compose -f docker-compose.dev.yml up -d
```

### Port Conflicts

If port `8000` or `5432` is busy, check for other running Docker projects or local services:

```bash
lsof -i :8000
```
