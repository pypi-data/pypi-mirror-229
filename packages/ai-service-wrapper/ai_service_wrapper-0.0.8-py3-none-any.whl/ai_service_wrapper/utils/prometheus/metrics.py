import prometheus_client
from prometheus_client import Counter, Histogram

CONTENT_TYPE_LATEST = str('text/plain; version=0.0.4; charset=utf-8')

REQUEST_COUNT = Counter(
    'request_count', 'App Request Count',
    ['appName', 'method', 'endpoint', 'httpStatus']
)
REQUEST_LATENCY = Histogram(
    'request_latency_seconds',
    'Request latency',
    ['appName', 'endpoint']
)

APIKEY_COUNT = Counter(
    'apikey_count', 'App apikey count',
    ['appName', 'apikey']
)