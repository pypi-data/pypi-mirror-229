import time
import requests
from . import logger

def apikey_tracking(request, service_name, apikey_service_host, response):
    try:
        response = requests.post(f"{apikey_service_host}/api-keys/auth-http",
                                    data={ 
                                    "apiKey": request.headers["x-api-key"], 
                                    "serviceName": service_name,
                                    "processTime": request.response_time,
                                    "isSuccess": False if 200 <= response.status < 300 else True,
                                    "requestAt": time.time() 
                                    })
        if 200 <= response.status_code < 300:
            logger.info("Success tracking apikey")
            return True
    except requests.exceptions.Timeout:
        pass
    except Exception as e:
        logger.error(str(e))
    
    return response