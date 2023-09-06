from fastapi import Request 
import time
import requests
from ai_service_wrapper.utils.prometheus.metrics import APIKEY_COUNT
from ai_service_wrapper.utils.logger import setup_logger

logger = setup_logger("Middleware")

async def RequestProcessTimeMiddleware(request: Request, call_next): 
    start_time = time.time()
    response = await call_next(request)
    response_time = time.time() - start_time
    request.state.response_time = response_time
    logger.info("Time took to process the request and return response is {} sec".format(response_time))
    return response

async def PrometheusHookMiddleware(request: Request, call_next):
    apikey = request.headers.get('x-api-key', "No Apikey")
    APIKEY_COUNT.labels('app', apikey).inc()
    response = await call_next(request)
    
    return response

async def ApikeyTrackingMiddleware(service_name, apikey_service_host, request: Request, call_next):
    response = await call_next(request)
    try:
        tracking_response = requests.post(f"{apikey_service_host}/api-keys/auth-http",
                                    data={ 
                                    "apiKey": request.headers["x-api-key"], 
                                    "serviceName": service_name,
                                    "processTime": request.state.response_time,
                                    "isSuccess": False if 200 <= response.status_code < 300 else True,
                                    "requestAt": time.time() 
                                    })
        if 200 <= tracking_response.status_code < 300:
            logger.info("Success tracking apikey")
            return True
    except requests.exceptions.Timeout:
        pass
    except Exception as e:
        logger.error(e)
    
    return response 