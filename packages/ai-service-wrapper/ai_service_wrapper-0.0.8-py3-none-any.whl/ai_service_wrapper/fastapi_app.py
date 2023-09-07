from functools import partial
import prometheus_client
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI, Request
from fastapi.responses import Response
from ai_service_wrapper.utils.prometheus.metrics import CONTENT_TYPE_LATEST
from .apisignature.decorators import async_fast_api_signature_required 
from .apisignature.sign import create_sign_header
from .utils.fastapi.exceptions import BadRequestException, bad_request_exception_handler 
from .utils.fastapi.middlewares import ( 
    PrometheusHookMiddleware, 
    ApikeyTrackingMiddleware,
    RequestProcessTimeMiddleware
)
from .utils.fastapi.http_scheme import HttpResonse

class FastAiServiceWrapper:

    def __init__(self, 
                 app: FastAPI, 
                 service_name, 
                 private_key_file,
                 apikey_service_host): 
        
        self.app = app
        self.service_name = service_name
        self.private_key_file = private_key_file
        self.apikey_service_host = apikey_service_host
        Instrumentator().instrument(app).expose(app)
        self.apply_exception_handler()
        self.apply_middleware()
        
        @app.get('/health')
        async def health():
            return HttpResonse.success(message="Ok", status_code=200)

        @app.get('/metrics/')
        async def metrics():
            return Response(prometheus_client.generate_latest(), media_type=CONTENT_TYPE_LATEST) 
            
        @app.get("/test-api-signature")
        @async_fast_api_signature_required(
            private_key_file=self.private_key_file,
            apikey_service_host=self.apikey_service_host
        )
        async def test_api_signature(request: Request):
            return HttpResonse.success(None, "Ok", 200)

        @app.post("/sign-api-signature") 
        def sign_api_signature(request: Request):
            apikey = request.headers.get("x-api-key")
            if not apikey:
                return HttpResonse.fail(None, "No api key provided", 403)
            headers = create_sign_header(apikey=apikey)
            return HttpResonse.success(headers, "Sign success!", 200)
    
    def apply_exception_handler(self):
        self.app.add_exception_handler(BadRequestException, bad_request_exception_handler)
    
    def apply_middleware(self):
        self.app.middleware('response_time')(RequestProcessTimeMiddleware)

        ApikeyTrackingMiddlewareFunc = partial(ApikeyTrackingMiddleware, 
                                           self.service_name, 
                                           self.apikey_service_host)
        self.app.middleware('apikey_tracking')(ApikeyTrackingMiddlewareFunc)

        self.app.middleware('http')(PrometheusHookMiddleware)

