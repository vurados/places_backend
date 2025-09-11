from prometheus_client import Counter, Histogram, generate_latest, REGISTRY
from prometheus_client.openmetrics.exposition import CONTENT_TYPE_LATEST
from fastapi import Request, Response
import time

# Метрики для HTTP запросов
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'http_status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint']
)

# Метрики для бизнес-логики
USER_REGISTRATION_COUNT = Counter(
    'user_registrations_total',
    'Total number of user registrations'
)

FRIEND_REQUEST_COUNT = Counter(
    'friend_requests_total',
    'Total number of friend requests'
)

MESSAGE_SENT_COUNT = Counter(
    'messages_sent_total',
    'Total number of messages sent'
)

# Middleware для сбора метрик
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    method = request.method
    endpoint = request.url.path
    
    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception as e:
        status_code = 500
        raise e
    finally:
        latency = time.time() - start_time
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, http_status=status_code).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(latency)
    
    return response

# Эндпоинт для сбора метрик
async def metrics_endpoint():
    return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)