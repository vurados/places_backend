# ArgoCD Integration Guide

This guide details how to set up and use ArgoCD for GitOps deployment of the `places-backend` application.

## Prerequisites

- A running Kubernetes cluster (e.g., Minikube, Kind, or a cloud provider).
- `kubectl` configured to point to your cluster.

## 1. Installation

We have provided a helper script to install ArgoCD and set up the namespace.

```bash
./deployments/scripts/install_argocd.sh
```

This script will:

1. Create the `argocd` namespace.
2. Apply the official install manifests.
3. Wait for the components to be ready.

## 2. Accessing the UI

### Get the Password

The initial admin password is stored in a secret. Retrieve it with:

```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo
```

### Port Forwarding

To access the UI locally:

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

- **URL**: `https://localhost:8080`
- **Username**: `admin`
- **Password**: (The one retrieved above)

## 3. Deploying the Application

We use an `Application` CRD to tell ArgoCD to manage our Helm chart.

```bash
kubectl apply -f argocd/application.yaml
```

This will create an Application named `places-backend` in ArgoCD, pointing to the `charts/places-backend` directory in this repository on the `feat/argoCD` branch.

**Note**: Once merged to main, update `targetRevision` in `argocd/application.yaml` to `HEAD` or `main`.

## 4. Sync Policy & Waves

The application is configured with:

- **Automated Sync**: Changes to the git repo are automatically applied.
- **Prune**: Resources removed from git are removed from the cluster.
- **Self-Heal**: Deviation from the desired state in the cluster is corrected automatically.

### Sync Waves

To ensure a stable startup, we use **ArgoCD Sync Waves**:

- **Wave 0**: Core dependencies (PostgreSQL, Redis, MinIO) and their ConfigMaps/Secrets.
- **Wave 1**: Database Migrations Job (runs migrations once DB is ready).
- **Wave 2**: Main Application Deployment (starts once migrations are complete).

### Dependency Waiting (Init Containers)

Both the Migration Job and the Application use `initContainers` to wait for TCP connectivity to PostgreSQL, Redis, and MinIO before starting. This prevents "Database not ready" and "AccessKeyId" errors during initial reconciliation.
