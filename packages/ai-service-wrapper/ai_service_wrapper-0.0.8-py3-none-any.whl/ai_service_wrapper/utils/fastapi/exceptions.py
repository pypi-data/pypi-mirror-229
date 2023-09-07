from typing import Any, Optional, Dict
from fastapi import FastAPI, HTTPException
from .http_scheme import HttpResonse

app = FastAPI()

class BadRequestException(HTTPException):
    
    def __init__(
        self,
        detail: Any = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(status_code=400, detail=detail, headers=headers)

def bad_request_exception_handler(request, exc):
    return  HttpResonse.fail(data=None, message=exc.detail, status_code=400)