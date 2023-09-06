import time

from flask import request

from ..prometheus import metrics

def start_timer():
    request.start_time = time.time()

def get_request_info():
    apikey = request.headers.get('x-api-key', "No Apikey")
    metrics.APIKEY_COUNT.labels('app', apikey).inc()

def stop_timer(res):
    response_time = time.time() - request.start_time
    metrics.REQUEST_LATENCY.labels('app', request.path).observe(response_time)
    return res

def record_request_data(res):
    metrics.REQUEST_COUNT.labels('app', request.method, request.path, res.status_code).inc()
    return res

def setup_metrics():
    before_request_func = []
    before_request_func.append(start_timer)
    before_request_func.append(get_request_info)

    after_request_func = []
    after_request_func.append(record_request_data)
    after_request_func.append(stop_timer)

    return before_request_func, after_request_func