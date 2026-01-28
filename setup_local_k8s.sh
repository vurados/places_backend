#!/usr/bin/env bash
set -e

echo "=== Building Docker Image ==="
docker build -t places_backend-app:latest .

echo "=== Loading Image into Minikube ==="
if minikube status | grep -q "Running"; then
    minikube image load places_backend-app:latest
else
    echo "Minikube is not running! Please wait for it to start."
    exit 1
fi

echo "=== Enabling Ingress Addon ==="
minikube addons enable ingress

echo "=== Enabling Metrics Server Addon ==="
minikube addons enable metrics-server

echo "=== Applying Manifests ==="
kubectl apply -f k8s/base.yml

# We delete the job first because k8s won't re-run a completed Job with the same name
kubectl delete job migrations -n places-backend --ignore-not-found

kubectl apply -f k8s/

echo "=== Setup Complete! ==="
echo "Please add the following line to your /etc/hosts file:"
MINIKUBE_IP=$(minikube ip)
echo "$MINIKUBE_IP api.places.internal"
echo ""
echo "Then you can access the API at http://api.places.internal"
