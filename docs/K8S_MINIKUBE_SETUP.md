# Local Kubernetes Setup with Minikube

This guide walks you through setting up the `places_backend` project in a local Kubernetes environment using Minikube.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed and running.
- [Minikube](https://minikube.sigs.k8s.io/docs/start/) installed.
- [kubectl](https://kubernetes.io/docs/tasks/tools/) installed and configured.

## Step 1: Start Minikube

Start the local cluster using the Docker driver:

```bash
minikube start --driver=docker
```

## Step 2: Enable Necessary Addons

Enable the Ingress controller and Metrics Server for monitoring and resource scaling:

```bash
minikube addons enable ingress
minikube addons enable metrics-server
```

## Step 3: Build and Load Docker Image

Build the application image locally and load it directly into Minikube's internal registry. This avoids the need for a remote registry.

```bash
# Build the image
docker build -t places_backend-app:latest .

# Load into Minikube
minikube image load places_backend-app:latest
```

> [!NOTE]
> The image name `places_backend-app:latest` must match the `image` field in `k8s/app.yml`.

## Step 4: Deploy Manifests

Apply all Kubernetes manifests from the `k8s/` directory:

```bash
kubectl apply -f k8s/
```

> [!TIP]
> `kubectl` will automatically process all files in the directory. Since the namespace is defined in `base.yml`, it will be created along with the other resources.

## Step 5: Configure Hosts

To access the application via the configured domain, add the Minikube IP to your `/etc/hosts` file.

1. Get the Minikube IP:

    ```bash
    minikube ip
    ```

2. Add the following line (replace `<MINIKUBE_IP>` with the actual address) or use ip for accessing the application:

    ```text
    <MINIKUBE_IP> api.places.internal
    ```

## Step 6: Verify Deployment

Check the status of the pods:

```bash
kubectl get pods -n places-backend
```

Once all pods are in the `Running` state, you can access:

- **API Documentation**: [http://api.places.internal/docs](http://api.places.internal/docs)
- **Health Check**: [http://api.places.internal/health/ready](http://api.places.internal/health/ready)
