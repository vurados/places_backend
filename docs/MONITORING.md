# Monitoring Guide

Complete guide to setting up and using monitoring for the Urban Places Backend.

## Overview

The project includes a comprehensive monitoring stack:

- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **Alertmanager**: Alert management  
- **Exporters**: Node, PostgreSQL, Redis, Blackbox
- **Telegram Integration**: Alert notifications via Telegram bot

---

## Quick Start

### Start Monitoring Stack

```bash
# Start with monitoring and portainer services
docker compose -f compose/docker-compose.yml -f compose/docker-compose.monitoring.yml --profile monitoring --profile portainer up -d
```

### Access Monitoring Tools (Production/Review)

For security, monitoring tools are **not exposed** to the public internet. Access them via a secure SSH tunnel.

#### 1. Configure Local DNS

Add to your local `/etc/hosts` (macOS/Linux) or `C:\Windows\System32\drivers\etc\hosts`:

```
127.0.0.1 grafana.internal portainer.internal prometheus.internal alertmanager.internal
```

#### 2. Open Tunnel

Run the helper script and enter your VPS credentials:

```bash
./deployments/scripts/connect_internal.sh
```

#### 3. Access URLs

| Service | Secure URL |
|---------|------------|
| Grafana | <http://grafana.internal:8080> |
| Prometheus | <http://prometheus.internal:8080> |
| Alertmanager | <http://alertmanager.internal:8080> |
| Portainer | <http://portainer.internal:8080> |

---

## Metrics

### Application Metrics

The FastAPI application exposes Prometheus metrics at:

```
http://localhost:8000/metrics
```

**Available Metrics:**

- `http_requests_total` - Total HTTP requests (labeled by method, endpoint, status)
- `http_request_duration_seconds` - Request latency histogram
- `user_registrations_total` - Counter for user registrations
- `friend_requests_total` - Counter for friend requests
- `messages_sent_total` - Counter for sent messages

### System Metrics

**Node Exporter** (port 9100):

- CPU usage
- Memory usage
- Disk I/O
- Network traffic

**PostgreSQL Exporter** (port 9187):

- Active connections
- Query performance
- Database size
- Transaction rates

**Redis Exporter** (port 9121):

- Memory usage
- Connected clients
- Commands processed
- Cache hit/miss ratio

---

## Prometheus Configuration

### Scrape Targets

Edit `deployments/configs/monitoring/prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'fastapi'
    static_configs:
      - targets: ['app:8000']
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

### Query Examples

```promql
# Request rate
rate(http_requests_total[5m])

# 95th percentile latency
histogram_quantile(0.95, http_request_duration_seconds_bucket)

# Error rate
rate(http_requests_total{http_status=~"5.."}[5m])
```

---

## Grafana Dashboards

### Import Pre-built Dashboards

1. Open Grafana: <http://localhost:3000>
2. Go to **Dashboards** → **Import**
3. Enter dashboard ID or upload JSON

**Recommended Dashboards:**

- **Node Exporter Full** (ID: 1860)
- **PostgreSQL Database** (ID: 9628)
- **Redis Dashboard** (ID: 11835)
- **FastAPI Observability** (Custom, see below)

### Custom FastAPI Dashboard

Create a new dashboard with panels:

**HTTP Request Rate:**

```promql
sum(rate(http_requests_total[5m])) by (method, endpoint)
```

**Response Time (p95):**

```promql
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
```

**Error Rate:**

```promql
sum(rate(http_requests_total{http_status=~"5.."}[5m]))
```

---

## Alerting

### Alert Rules

Alerts are defined in `deployments/configs/monitoring/prometheus.yml`:

```yaml
groups:
  - name: api_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{http_status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"

      - alert: HighMemoryUsage
        expr: node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes < 0.1
        for: 5m
        labels:
          severity: critical
```

### Telegram Notifications

#### 1. Create Telegram Bot

1. Message [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow instructions
3. Save the bot token

#### 2. Get Chat ID

1. Message your bot
2. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Look for `chat.id` in the response

#### 3. Configure Environment

Add to `.env`:

```env
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=123456789
```

#### 4. Restart Services

```bash
docker compose -f docker-compose.monitoring.yml restart alertmanager-telegram
```

### Test Alert

Trigger a test alert:

```bash
curl -X POST http://localhost:9093/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '[{
    "labels": {
      "alertname": "TestAlert",
      "severity": "warning"
    },
    "annotations": {
      "summary": "This is a test alert"
    }
  }]'
```

---

## Advanced Configuration

### Retention Period

Prometheus data retention (in `compose/docker-compose.monitoring.yml`):

```yaml
prometheus:
  command:
    - '--storage.tsdb.retention.time=200h'  # 8 days
```

### Grafana Provisioning

Auto-configure data sources and dashboards:

```
deployments/configs/monitoring/grafana/provisioning/
├── datasources/
│   └── prometheus.yml
└── dashboards/
    └── dashboards.yml
```

### Custom Metrics

Add custom business metrics in your code:

```python
from prometheus_client import Counter

# In your service
payment_counter = Counter('payments_total', 'Total payments processed')

async def process_payment():
    # ... payment logic
    payment_counter.inc()
```

---

## Production Best Practices

### Security

1. **Restrict Access**: Use Nginx auth for Grafana/Prometheus
2. **HTTPS**: Enable TLS for all monitoring endpoints
3. **Firewall**: Block exporter ports (9100, 9187, 9121) from public internet

### Storage

1. **External Volume**: Mount Prometheus data to persistent storage
2. **Backup**: Regularly backup Prometheus data directory
3. **Long-term Storage**: Consider Thanos or Victoria Metrics for long-term retention

### Performance

1. **Scrape Interval**: Adjust based on needs (default: 15s)
2. **Recording Rules**: Pre-calculate expensive queries
3. **Pruning**: Regularly review and remove unused metrics

---

## Troubleshooting

### Prometheus Not Scraping

**Check targets:**

Visit <http://localhost:9090/targets>

**Common issues:**

- Service not exposing metrics endpoint
- Network connectivity between containers
- Incorrect scrape configuration

### Grafana Dashboard Empty

**Check:**

1. Data source configured correctly
2. Time range includes recent data
3. Query syntax is valid

**Test query in Prometheus first** (<http://localhost:9090/graph>)

### No Alert Notifications

**Verify:**

1. Alertmanager is running: `docker ps | grep alertmanager`
2. Telegram bot token is correct
3. Check Alertmanager logs: `docker logs places_backend-alertmanager-1`

---

## Example Queries

### Application Performance

```promql
# Average request latency by endpoint
avg(http_request_duration_seconds) by (endpoint)

# Requests per second
sum(rate(http_requests_total[1m]))

# Success rate
sum(rate(http_requests_total{http_status!~"5.."}[5m])) 
/ 
sum(rate(http_requests_total[5m]))
```

### Database Performance

```promql
# Active connections
pg_stat_database_numbackends{datname="places_db"}

# Query duration
rate(pg_stat_statements_mean_exec_time_seconds[5m])

# Database size
pg_database_size_bytes{datname="places_db"}
```

### System Resources

```promql
# CPU usage
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory usage
(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100

# Disk usage
(node_filesystem_size_bytes - node_filesystem_avail_bytes) / node_filesystem_size_bytes * 100
```

---

## Integration with CI/CD

### GitLab CI Monitoring

Add monitoring check to CI pipeline:

```yaml
monitoring_check:
  stage: verify
  script:
    - curl -f http://prometheus:9090/-/healthy || exit 1
    - curl -f http://grafana:3000/api/health || exit 1
  only:
    - main
```

---

## Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [PromQL Guide](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Best Practices for Metrics](https://prometheus.io/docs/practices/)

---

## Next Steps

1. **Set up alerts** for critical metrics
2. **Create dashboards** for your team
3. **Configure Telegram** notifications
4. **Review metrics** regularly
5. **Optimize queries** for performance
