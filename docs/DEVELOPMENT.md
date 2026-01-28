# Development Guide

Guide for setting up local development environment and contributing to the project.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Setup](#local-setup)
- [Database Migrations](#database-migrations)
- [Running Tests](#running-tests)
- [Code Style](#code-style)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

---

## Prerequisites

### Required Software

- **Python 3.12+**
- **Docker & Docker Compose**
- **Git**
- **Poetry** (optional, for dependency management)

### Recommended Tools

- **VS Code** with Python extension
- **Postman** or **HTTPie** for API testing
- **DBeaver** or **pgAdmin** for database management

---

## Local Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd places_backend
```

### 2. Create Virtual Environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
pip install -r app/requirements.txt
```

### 4. Set Up Environment

```bash
cp .env.example .env
```

Edit `.env` with your local configuration:

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=test_user
DB_PASSWORD=test_password
DB_NAME=places_db

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin

# Security
SECRET_KEY=your-secret-key-here
```

### 5. Start Services

```bash
docker compose -f compose/docker-compose.dev.yml up -d
```

This starts:

- PostgreSQL on `localhost:5432`
- Redis on `localhost:6379`
- MinIO on `localhost:9000` (API) and `localhost:9001` (Console)

### 6. Run Migrations

```bash
cd app
alembic upgrade head
```

### 7. Start Development Server

```bash
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Visit:

- API: <http://localhost:8000>
- Docs: <http://localhost:8000/docs>

---

## Database Migrations

### Create a New Migration

```bash
cd app
alembic revision --autogenerate -m "Add user profile fields"
```

This generates a migration file in `app/alembic/versions/`.

### Review Migration

Always review auto-generated migrations:

```bash
# View the generated file
cat app/alembic/versions/xxxx_add_user_profile_fields.py
```

### Apply Migrations

```bash
alembic upgrade head
```

### Rollback Migration

```bash
# Rollback one version
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision_id>
```

### View Migration History

```bash
alembic history
alembic current
```

---

## Running Tests

### Full Test Suite

```bash
# Using Docker Compose
docker compose -f compose/docker-compose.test.yml up --build

# Or locally
cd app
pytest -v
```

### Run Specific Tests

```bash
# Single file
pytest app/tests/test_auth.py -v

# Single test function
pytest app/tests/test_auth.py::test_register_user -v

# With coverage
pytest --cov=app --cov-report=html
```

### Test Database

Tests use a separate test database automatically configured in `conftest.py`:

- Database: `test_db`
- Migrations are applied before tests
- Database is cleaned after each test

---

## Code Style

### Python Style Guide

This project follows **PEP 8** with some modifications:

- Line length: 100 characters
- Use type hints
- Docstrings for all public functions/classes

### Formatting Tools

**Black** (code formatter):

```bash
black app/
```

**isort** (import sorting):

```bash
isort app/
```

**flake8** (linting):

```bash
flake8 app/
```

### Pre-commit Hooks

Install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

This automatically runs formatters and linters before each commit.

---

## Project Structure

```
places_backend/
├── ansible/              # Deployment automation (roles, playbooks, inventories)
├── app/                  # FastAPI Application code
├── compose/              # Docker Compose files
├── deployments/          # Deployment-related files
│   ├── configs/          # Configuration files (nginx, monitoring, ssl)
│   └── scripts/          # Deployment and utility scripts
├── docker/               # Dockerfiles
├── docs/                 # Documentation
└── README.md
```

### Key Directories

- **`app/api/endpoints/`**: Individual route modules
- **`app/models/`**: Database models (ORM)
- **`app/schemas/`**: Request/response schemas (validation)
- **`app/services/`**: Business logic (keep endpoints thin)
- **`app/tests/`**: Test suite

---

## Contributing

### Workflow

1. **Create a branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes**
   - Write code
   - Add tests
   - Update documentation

3. **Run tests**

   ```bash
   docker compose -f compose/docker-compose.test.yml up --build
   ```

4. **Format code**

   ```bash
   black app/
   isort app/
   ```

5. **Commit**

   ```bash
   git add .
   git commit -m "feat: add user profile feature"
   ```

6. **Push**

   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create Pull/Merge Request**

### Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding/updating tests
- `chore:` Maintenance tasks

**Examples:**

```
feat: add friend request notifications
fix: resolve database connection timeout
docs: update API documentation for places endpoint
```

### Code Review Checklist

- [ ] Code follows style guide
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No sensitive data in commits
- [ ] Migration files are reviewed
- [ ] Backward compatibility considered

---

## Debugging

### VS Code Launch Configuration

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
      ],
      "jinja": true,
      "justMyCode": false
    }
  ]
}
```

### Database Debugging

Connect to PostgreSQL:

```bash
docker exec -it places_backend-db-1 psql -U test_user -d places_db
```

Useful SQL commands:

```sql
-- List tables
\dt

-- View table structure
\d users

-- Query data
SELECT * FROM users LIMIT 10;
```

### Logs

View application logs:

```bash
# Docker logs
docker logs places_backend-app-1 -f

# Application logs (inside container)
docker exec -it places_backend-app-1 tail -f /app/logs/app.log
```

---

## Performance Tips

### Database Indexing

Add indexes for frequently queried fields:

```python
# models/place.py
class Place(Base):
    __tablename__ = "places"
    
    # Add index
    __table_args__ = (
        Index('ix_places_location', 'lat', 'lon'),
    )
```

### Async Operations

Use async/await for I/O operations:

```python
# Good
async def get_places(db: AsyncSession):
    result = await db.execute(select(Place))
    return result.scalars().all()

# Avoid blocking operations
```

### Caching

Use Redis for caching:

```python
from app.core.cache import redis_client

async def get_popular_places():
    cached = await redis_client.get("popular_places")
    if cached:
        return json.loads(cached)
    
    # Fetch from database
    places = await fetch_from_db()
    await redis_client.setex("popular_places", 3600, json.dumps(places))
    return places
```

---

## Accessing Internal Tools

For security, administrative tools (Grafana, Portainer, etc.) are **not exposed to the public internet**. They are bound to `localhost` on the server and must be accessed via a secure SSH tunnel.

### 1. Setup Local DNS

Add the following to your local `/etc/hosts` file (macOS/Linux) or `C:\Windows\System32\drivers\etc\hosts`:

```
127.0.0.1 grafana.internal portainer.internal prometheus.internal alertmanager.internal
```

### 2. Connect Tunnel

Run the helper script:

```bash
./deployments/scripts/connect_internal.sh
```

Follow the prompts to enter your server user and IP (defaults to Vagrant settings).

### 3. Access Tools

Once connected, access tools in your browser:

- **Grafana**: <http://grafana.internal:8080>
- **Portainer**: <http://portainer.internal:8080>
- **Prometheus**: <http://prometheus.internal:8080>
- **Alertmanager**: <http://alertmanager.internal:8080>

---

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Database Connection Issues

```bash
# Check if database is running
docker ps | grep postgres

# Restart database
docker restart places_backend-db-1
```

### Migration Conflicts

```bash
# Reset alembic history (CAUTION: development only!)
alembic downgrade base
rm app/alembic/versions/*.py
alembic revision --autogenerate -m "Initial"
alembic upgrade head
```

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
