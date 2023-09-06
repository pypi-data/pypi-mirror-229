import time
from .endecrypt import encrypt

def sign(timestamp, apikey):
    payload = f"{timestamp}{'@@@'}{apikey}" 
    signature = encrypt(bytes(payload, 'utf-8'))
    return signature

def create_sign_header(apikey):
    timestamp = time.time()
    headers = {
        "x-api-signature": sign(timestamp, apikey),
        "x-api-timestamp": timestamp,
        "x-api-key": apikey
    }
    return headers