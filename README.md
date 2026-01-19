# Urban Places Social App - Backend

A FastAPI-based backend for a social application focused on urban places, routes, and location-based features.

## 🏗️ Architecture

### Tech Stack

- **Framework**: FastAPI (Python 3.12)
- **Database**: PostgreSQL 15 with asyncpg
- **Cache**: Redis 7
- **Storage**: MinIO (S3-compatible object storage)
- **Reverse Proxy**: Nginx with SSL/TLS
- **Monitoring**: Prometheus + Grafana
- **Migrations**: Alembic
- **Testing**: Pytest with async support

### Key Features

- User authentication with JWT tokens
- Friend system and messaging
- Location-based place discovery
- Route planning and collections
- Photo uploads with MinIO
- Real-time notifications
- Comprehensive monitoring and metrics

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- (Optional) Vagrant for local deployment testing

### Local Development

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd places_backend
   ```

2. **Set up environment**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start services**

   ```bash
   docker compose up -d
   ```

4. **Run migrations**

   ```bash
   docker exec -it places_backend-app-1 alembic upgrade head
   ```

5. **Access the API**
   - API: <http://localhost:8000>
   - Interactive docs: <http://localhost:8000/docs>
   - Health check: <http://localhost:8000/health>

## 📝 Environment Variables

Key environment variables (see [`.env.example`](.env.example) for full list):

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | PostgreSQL host | `db` |
| `DB_USER` | Database user | `test_user` |
| `DB_PASSWORD` | Database password | - |
| `DB_NAME` | Database name | `places_db` |
| `REDIS_HOST` | Redis host | `redis` |
| `REDIS_PASSWORD` | Redis password | - |
| `MINIO_ENDPOINT` | MinIO endpoint | `minio:9000` |
| `SECRET_KEY` | JWT secret key | - |

## 🧪 Testing

### Run all tests

```bash
docker compose -f docker-compose.test.yml up --build
```

### Run specific test file

```bash
docker exec -it places_backend-tests pytest app/tests/test_auth.py -v
```

## 📊 Monitoring

The project includes comprehensive monitoring with Prometheus and Grafana.

### Start monitoring stack

```bash
docker compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
```

### Access monitoring tools

- **Prometheus**: <http://localhost:9090>
- **Grafana**: <http://localhost:3000> (admin/admin)
- **Metrics endpoint**: <http://localhost:8000/metrics>

See [`docs/MONITORING.md`](docs/MONITORING.md) for detailed setup and dashboard configuration.

## 🚢 Deployment

### Vagrant (Local Testing)

Test the Ansible deployment locally:

```bash
cd deployments
./test_deploy.sh
```

Access deployed app: <https://192.168.56.2/health>

### Production (Ansible)

See [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) for complete deployment guide.

## 📁 Project Structure

```
places_backend/
├── app/
│   ├── alembic/          # Database migrations
│   ├── api/              # API routes
│   ├── core/             # Core configuration
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   └── tests/            # Test suite
├── deployments/
│   ├── ansible/          # Ansible playbooks
│   ├── monitoring/       # Monitoring configs
│   └── nginx/            # Nginx configurations
├── docs/                 # Documentation
├── docker-compose.yml    # Main compose file
├── docker-compose.monitoring.yml  # Monitoring stack
├── docker-compose.test.yml        # Test environment
└── Vagrantfile           # Local VM for testing
```

## 🛠️ Development

### Database Migrations

Create a new migration:

```bash
docker exec -it places_backend-app-1 alembic revision --autogenerate -m "Description"
```

Apply migrations:

```bash
docker exec -it places_backend-app-1 alembic upgrade head
```

### API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>

For detailed API documentation, see [`docs/API.md`](docs/API.md).

## 🔐 Security

- JWT-based authentication
- Password hashing with bcrypt
- HTTPS with Let's Encrypt (production)
- Self-signed certificates (development)
- Rate limiting via Nginx
- Secrets managed with Ansible Vault

## 📚 Documentation

- [Deployment Guide](docs/DEPLOYMENT.md) - Ansible deployment and Vagrant testing
- [API Documentation](docs/API.md) - Endpoints and authentication
- [Development Guide](docs/DEVELOPMENT.md) - Local setup and contributing
- [Monitoring Guide](docs/MONITORING.md) - Prometheus and Grafana setup

## 🔄 CI/CD

This project uses GitLab CI for continuous integration and deployment.

### Pipeline Stages

1. **Test**: Run pytest suite
2. **Deploy**: Deploy to VPS using Ansible (production only)

See [`.gitlab-ci.yml`](.gitlab-ci.yml) for pipeline configuration.

## 📄 License

[Your License Here]

## 🤝 Contributing

See [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) for contribution guidelines.
