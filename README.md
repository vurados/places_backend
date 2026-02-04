# Urban Places Social App - Backend

A FastAPI-based backend for a social application focused on urban places, routes, and location-based features.

## Alternative Implementations

This project includes alternative architectural approaches in dedicated branches:

| Branch | Topic | Implementation Details |
| :--- | :--- | :--- |
| **[`feat-hcorpvault`](../../tree/feat-hcorpvault)** | **Secret Management** | Uses **HashiCorp Vault** for centralized secret storage, AppRole authentication, and dynamic configuration via Vault Agent templates. |
| **[`feat-k8s`](../../tree/feat-k8s)** | **Orchestration** | Migration to **Kubernetes** with HPA (Horizontal Pod Autoscaling), PDB (PodDisruptionBudgets), and K8s Jobs for automated migrations. |

## Architecture

```mermaid
graph TD
    User([User]) -->|HTTPS:443| Nginx[Nginx]
    Nginx -->|Proxy| FastAPI[app: FastAPI]
    FastAPI --> Redis[(Redis: Cache)]
    FastAPI --> DB[(PostgreSQL: DB)]
    FastAPI --> MinIO[MinIO: S3 Storage]
```

### Tech Stack

- **Framework**: FastAPI (Python 3.12)
- **Database**: PostgreSQL 15 (Async)
- **Cache**: Redis 7
- **Storage**: MinIO (S3-compatible)
- **Reverse Proxy**: Nginx with SSL/TLS
- **Orchestration**: Ansible + Docker Compose
- **Monitoring**: Prometheus + Grafana

### Key Features

- **Authentication**: JWT-based secure auth and session management.
- **Social**: Friend systems, real-time messaging, and notifications.
- **Geography**: Location-based discovery and route planning.
- **Storage**: Multi-media support with S3-compatible object storage.
- **Operations**: Built-in monitoring, metrics, and automated deployment.

## Quick Start

### 1. Set Up Services For Backend Development

```bash
cp .env.example .env
docker compose -f docker-compose.dev.yml up -d
```

### 2. Access the Project

- **Interactive API Docs**: <http://localhost:8000/docs>
- **Health Check**: <http://localhost:8000/health>
- **Metrics**: <http://localhost:8000/metrics>

> [!TIP]
> For a better development experience, including tests and code style guides, refer to the **[Backend Development Guide](docs/DEVELOPMENT_BACKEND.md)**.

## Testing

Run the full test suite using the dedicated test environment:

```bash
docker compose -f docker-compose.test.yml up --build
```

---

## CI/CD

This project uses **GitHub Actions** for:

- **CI**: Automated testing and security scanning (`bandit`).
- **CD**: Automated production deployment via Ansible.

---

## Documentation Index

| Guide | Description |
| --- | --- |
| **[API Reference](docs/API.md)** | Endpoints, request/response schemas, and auth. |
| **[Backend Development](docs/DEVELOPMENT_BACKEND.md)** | Rapid development workflow with Docker (hot-reload). |
| **[Infrastructure & DevOps](docs/DEVELOPMENT_DEVOPS.md)** | Testing full stack with Vagrant and Ansible. |
| **[Deployment Guide](docs/DEPLOYMENT.md)** | Production setup, SSL, and CI/CD pipelines. |
| **[Monitoring](docs/MONITORING.md)** | Prometheus, Grafana dashboards, and alerting. |

---

## License

[Your License Here]
