# Kubernetes Monitoring & Observability

This guide covers the monitoring and autoscaling features of the `places_backend` in a Kubernetes environment.

## 1. Metrics Server (Resource Monitoring)

We use the [Kubernetes Metrics Server](https://github.com/kubernetes-sigs/metrics-server) (enabled as a Minikube addon) to collect resource usage metrics (CPU/Memory).

### Basic Commands

Monitor current resource usage of your pods:

```bash
kubectl top pods -n places-backend
```

Monitor your nodes:

```bash
kubectl top nodes
```

---

## 2. Horizontal Pod Autoscaler (HPA)

The application is configured to scale automatically based on resource utilization.

### Configuration

The HPA is defined in [`k8s/hpa.yml`](../k8s/hpa.yml). It targets:

- **CPU**: 70% average utilization.
- **Memory**: 80% average utilization.
- **Replicas**: 2 (min) to 5 (max).

### Check HPA Status

```bash
kubectl get hpa -n places-backend
```

### Scaling Behavior

We have configured stabilization windows to prevent "flapping" (rapid scaling up and down):

- **Scale Up**: Immediate (0s stabilization) to handle burst traffic.
- **Scale Down**: 5-minute stabilization window to ensure quiet periods are sustained before removing pods.

---

## 3. Application Metrics (Prometheus)

The FastAPI application exposes Prometheus-compatible metrics at the `/metrics` endpoint.

### Accessing Metrics

If you want to view raw metrics from within the cluster:

```bash
kubectl exec -it deployment/places-backend -n places-backend -- curl http://localhost:8000/metrics
```

### Exposed Metrics

- `http_requests_total`: Total HTTP requests (by method, status, endpoint).
- `http_request_duration_seconds`: Latency histogram.
- Custom business metrics defined in `app/core/monitoring.py`.

---

## 4. Health Checks

Kubernetes uses three types of probes to manage container lifecycle:

| Probe | Path | Purpose |
| --- | --- | --- |
| **Liveness** | `/health/live` | Restarts the container if it becomes unresponsive. |
| **Readiness** | `/health/ready` | Stops sending traffic if the DB or Redis is disconnected. |
| **Startup** | `/health/live` | Gives the app time to finish migrations before liveness checks start. |

---

## 5. Logs

Access application logs using `kubectl`:

```bash
# Follow logs for all app replicas
kubectl logs -f -n places-backend -l app=places-backend
```

Logs are outputted in **JSON format** for easy processing by log aggregators like Fluentd or Loki.
