# Development Guide

Guide for setting up local development environment and contributing to the project.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Workflow Options](#choose-your-workflow)
- [Shared Information](#shared-information)

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

## Choose Your Workflow

The project supports two main development workflows depending on your focus.

### 1. [Backend Development](DEVELOPMENT_BACKEND.md)

**Recommended for most contributors.**

- Focus on: API, Business Logic, Models.
- Environment: Docker Compose (`docker-compose.dev.yml`).
- Pros: Fast iteration, instant code reload, lightweight.

### 2. [DevOps & Infrastructure](DEVELOPMENT_DEVOPS.md)

**Recommended for platform engineers.**

- Focus on: Ansible, Nginx, SSL, Monitoring, Deployment Scripts.
- Environment: Vagrant VM (`Vagrantfile`) + Ansible.
- Pros: Production-like environment, full stack verification.

---

---

## Shared Information

### Project Structure

See the specific guides for directory breakdowns, but generally:

- `app/`: Source code.
- `deployments/`: Infrastructure and CI/CD.
- `docs/`: Guides and API reference.

### Contributing

1. Create a feature branch.
2. Follow the workflow in your chosen guide.
3. Submit a Pull Request with passing tests.

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
