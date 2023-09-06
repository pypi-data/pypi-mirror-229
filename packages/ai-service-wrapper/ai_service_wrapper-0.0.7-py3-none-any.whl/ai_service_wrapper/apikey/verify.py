import time
import requests
import aiohttp
from . import logger

def verify_apikey_by_file(apikey, apikeys_file):
    with open(apikeys_file, "r") as file:
        apikeys = [ key.strip("\n") for key in file ]
        if apikey in apikeys:
            return True
    
    return False

def verify_apikey(apikey, apikey_service_host, retry=3):
    print(apikey_service_host)
    for _ in range(retry):
        try:
            response = requests.post(f"{apikey_service_host}/api-keys/auth-http",
                                     data={ 
                                        "key": apikey,
                                        "requestAt": time.time() 
                                        })
            if response.status_code == 200:
                logger.info("Success verify apikey from apikey service")
                return True
        except requests.exceptions.Timeout:
            pass
        except Exception as e:
            logger.error(str(e))
    
    return False

async def async_verify_apikey(apikey, apikey_service_host, retry=3):
    print(apikey_service_host)
    for _ in range(retry):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{apikey_service_host}/api-keys/auth-http",
                                            data={ 
                                                "key": apikey,
                                                "requestAt": time.time() 
                                                }) as response:

                    if response.status == 200:
                        logger.info("Success verify apikey from apikey service")
                        return True

        except Exception as e:
            logger.error(str(e))
    
    return False