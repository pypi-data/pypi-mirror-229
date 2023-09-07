import re
import time
from . import logger
from .endecrypt import decrypt
from ..apikey.verify import verify_apikey

def verify(signature, 
           timestamp, 
           apikey, 
           request_lifetime,
           apikey_service_host,
           private_key_file="ENV/private.pem"): 
    try:
        payload = decrypt(signature, private_key_file=private_key_file)
    except Exception as e:
        logger.error(e)
        return False, "Cannot decrypt the signature"

    match = re.fullmatch(r'(.*)@@@(.*)', payload)
    if not match:
        return False, "Payload structure does not match prefined payload structure"

    match_timestamp, match_apikey = match.groups()

    timestamp = timestamp.split(".")[0]
    match_timestamp = match_timestamp.split(".")[0]

    if len(timestamp) == 13:
        timestamp = timestamp[:10]

    if len(match_timestamp) == 13:
        match_timestamp= match_timestamp[:10]

    if not is_valid_timestamp(timestamp):
        return False, "Timestamp value is not valid type. Must be (float or int) timestamp value"
    
    timestamp = int(float(timestamp))
    match_timestamp = int(float(match_timestamp))

    if match_timestamp != timestamp:
        return False, "Timestamp in signature does not match the timestamp param"
    
    if match_apikey != apikey:
        return False, "Apikey in signature does not match the apikey param"

    now = time.time()
    if now - timestamp > request_lifetime:
        return False, "Exceed allowed request life time"

    try: 
        if not verify_apikey(apikey, apikey_service_host):
            return False, "Failed verify apikey"
    except Exception as e:
        logger.error(e)
        return False, "System error verify apikey"
    
    return True, "Success verify"

def verify_header(headers, private_key_file, apikey_service_host, request_lifetime=300):
    required_headers = [
        "x-api-key",
        "x-api-timestamp",
        "x-api-signature"
    ]

    for require_header in required_headers:
        value = headers.get(require_header)
        if not value:
            return False, "Headers does not included required param"

    return verify(headers.get("x-api-signature"),
                  headers.get("x-api-timestamp"),
                  headers.get("x-api-key"),
                  request_lifetime=request_lifetime,
                  private_key_file=private_key_file,
                  apikey_service_host=apikey_service_host,)
    
def is_valid_timestamp(timestamp):
    try:
        timestamp = float(timestamp)
        now = time.time()
        if 0 <= timestamp <= now+1:
            return True
        return False
    except Exception as e:
        logger.error(e)
        return False