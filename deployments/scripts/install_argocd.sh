#!/usr/bin/env bash

# Exit on error
set -e

# Configuration
ARGOCD_NAMESPACE="argocd"
ARGOCD_VERSION="v2.9.3" # Stable version compatible with most K8s versions

echo "Installing ArgoCD..."

# 1. Create Namespace
if ! kubectl get namespace "$ARGOCD_NAMESPACE" > /dev/null 2>&1; then
    echo "Creating namespace '$ARGOCD_NAMESPACE'..."
    kubectl create namespace "$ARGOCD_NAMESPACE"
else
    echo "Namespace '$ARGOCD_NAMESPACE' already exists."
fi

# 2. Install ArgoCD
echo "Applying ArgoCD manifests..."
kubectl apply -n "$ARGOCD_NAMESPACE" -f https://raw.githubusercontent.com/argoproj/argo-cd/"$ARGOCD_VERSION"/manifests/install.yaml

# 3. Patch Server Service to NodePort (Optional, for easier local access)
# For production, utilize Ingress. For this setup, we'll patch to NodePort or just use port-forward in docs.
# echo "Patching argocd-server service to NodePort..."
# kubectl patch svc argocd-server -n "$ARGOCD_NAMESPACE" -p '{"spec": {"type": "NodePort"}}'

# 4. Wait for components
echo "Waiting for ArgoCD components to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/argocd-server -n "$ARGOCD_NAMESPACE"
kubectl wait --for=condition=available --timeout=300s deployment/argocd-repo-server -n "$ARGOCD_NAMESPACE"
kubectl wait --for=condition=available --timeout=300s deployment/argocd-dex-server -n "$ARGOCD_NAMESPACE" || echo "Dex server might not be enabled by default or taking longer."

echo "ArgoCD installed successfully! 🎉"
echo "To access the UI:"
echo "1. Get the password:"
echo "   kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath=\"{.data.password}\" | base64 -d; echo"
echo "2. Port-forward:"
echo "   kubectl port-forward svc/argocd-server -n argocd 8080:443"
echo "3. Open https://localhost:8080 (Username: admin)"
