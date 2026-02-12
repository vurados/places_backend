# Helm Migration Strategy

This document outlines the strategy for migrating our existing Kubernetes manifests (`k8s/`) to a Helm chart. Helm allows us to template our manifests, manage releases, and handle dependencies more effectively.

## 1. Chart Structure

We will create a new chart named `places-backend`. The proposed directory structure is as follows:

```text
charts/places-backend/
├── Chart.yaml          # Metadata (name, version, description)
├── values.yaml         # Default configuration values
├── templates/          # K8s manifest templates
│   ├── deployment.yaml # From k8s/app.yml (Deployment)
│   ├── service.yaml    # From k8s/app.yml (Service)
│   ├── ingress.yaml    # From k8s/ingress.yml
│   ├── hpa.yaml        # From k8s/hpa.yml
│   ├── pdb.yaml        # From k8s/pdb.yml
│   ├── job-migrations.yaml # From k8s/migrations-job.yml
│   ├── configmap.yaml  # From k8s/base.yml (ConfigMap)
│   ├── secret.yaml     # From k8s/base.yml (Secret)
│   ├── _helpers.tpl    # Shared templates (labels, names)
│   └── tests/          # Helm tests
└── charts/             # Dependency charts (Subcharts)
```

## 2. Dependencies (Subcharts)

Instead of maintaining raw manifests for standard services, we should use official Helm charts as dependencies in `Chart.yaml`:

- **PostgreSQL**: `bitnami/postgresql` (Replace `k8s/db.yml`)
- **Redis**: `bitnami/redis` (Replace `k8s/redis.yml`)
- **MinIO**: `minio/minio` (Replace `k8s/minio.yml`)

This simplifies management and provides production-ready defaults.

## 3. Values Configuration (`values.yaml`)

We will extract hardcoded values from the manifests into `values.yaml` to allow for environment-specific overrides.

### Key Parameters

| Parameter | Description | Default |
| :--- | :--- | :--- |
| `image.repository` | Application image repo | `vurados/places-backend` |
| `image.tag` | Application image tag | `latest` |
| `replicaCount` | Number of pods | `3` |
| `service.port` | Service port | `8000` |
| `ingress.enabled` | Enable Ingress | `true` |
| `ingress.host` | Ingress hostname | `places.local` |
| `resources` | CPU/Memory limits | `{}` |
| `autoscaling.enabled` | Enable HPA | `true` |
| `postgresql.enabled` | Enable internal DB | `true` |
| `redis.enabled` | Enable internal Redis | `true` |
| `minio.enabled` | Enable internal MinIO | `true` |

## 4. Templating Strategy

### Deployment (`templates/deployment.yaml`)

- Use `{{ .Values.image.repository }}:{{ .Values.image.tag }}`.
- Loop over `{{ .Values.env }}` to set environment variables.
- Use `{{ include "places-backend.fullname" . }}` for resource names.

### Ingress (`templates/ingress.yaml`)

- Condition: `{{- if .Values.ingress.enabled -}}`.
- Loop over hosts and paths.

### ConfigMap/Secret

- Generate purely from `values.yaml` or external files.

## 5. Migration Steps

1. **Initialize Chart**:

    ```bash
    helm create charts/places-backend
    # Clean up default templates
    rm -rf charts/places-backend/templates/*
    ```

2. **Migrate Application Manifests**:
    - Copy `k8s/app.yml` to `templates/deployment.yaml` and `templates/service.yaml`.
    - Replace hardcoded values with `{{ .Values... }}` placeholders.

3. **Add Dependencies**:
    - Update `Chart.yaml` to include PostgreSQL, Redis, and MinIO.
    - Run `helm dependency update charts/places-backend`.

4. **Verify & Lint**:

    ```bash
    helm lint charts/places-backend
    helm template charts/places-backend --debug
    ```

5. **Install**:

    ```bash
    helm install places-backend charts/places-backend -n places-backend --create-namespace
    ```

## 6. GitOps Integration

This chart is fully integrated with **ArgoCD**. Refer to **[ArgoCD Guide](ARGOCD.md)** for automated deployment instructions.
