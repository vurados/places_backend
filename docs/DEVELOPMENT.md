# Backend Development Guide (Kubernetes)

This guide is for developers building and testing the `places_backend` application within a local Kubernetes environment.

## Prerequisites

- **Docker**: For building container images.
- **Minikube**: Local Kubernetes cluster.
- **kubectl**: Kubernetes command-line tool.
- **Python 3.12**: Local installation for IDE support (optional but recommended).

## Choose Your Workflow

### 1. Unified K8s Workflow (Recommended)

Run the entire stack in Minikube to ensure your changes work in a production-like environment.

- **Start here**: Follow the **[K8s Minikube Setup Guide](K8S_MINIKUBE_SETUP.md)**.
- **Pros**: Full environment parity, tests HPA and Ingress configurations.
- **Cons**: Image rebuilds required for code changes (automated via `setup_local_k8s.sh`).

### 2. Rapid Iteration (Local Development)

For rapid development of business logic, you can run the FastAPI app locally against the databases in Kubernetes.

1. **Forward Database Ports**:

    ```bash
    kubectl port-forward -n places-backend deployment/db 5432:5432
    kubectl port-forward -n places-backend deployment/redis 6379:6379
    ```

2. **Run FastAPI Locally**:

    ```bash
    # Set your .env to point to localhost
    export DB_HOST=localhost
    export REDIS_HOST=localhost
    uvicorn main:app --reload
    ```

---

## Project Structure

- `app/`: Source code including API, models, and business logic.
- `k8s/`: Kubernetes manifests (Deployments, Services, HPA, etc.).
- `docs/`: Guides and API reference.

## Testing

### Automated Tests in Kubernetes

Run the full test suite inside a running pod:

```bash
kubectl exec -it deployment/places-backend -n places-backend -- pytest
```

---

## Code Style

- **Formatting**: Use `black app/`.
- **Linting**: Use `flake8 app/`.
- **Imports**: Use `isort app/`.

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
