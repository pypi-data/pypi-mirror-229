from functools import partial
import prometheus_client
from flask import request, Response
from .apisignature.decorators import api_signature_required
from .apisignature.sign import create_sign_header
from .apikey.apikey_tracking import apikey_tracking 
from .utils.prometheus.metrics import CONTENT_TYPE_LATEST
from .utils.flask import setup_prometheus_hook
from .utils.flask.http_scheme import HttpResonse
from .utils.logger import setup_logger

logger = setup_logger("AiServiceWrapper")

class FlaskAiServiceWrapper:

    def __init__(self, 
                 app, 
                 service_name,
                 apikey_service_host=None): 

        self.app = app
        before_request_func = []
        after_request_func = []
        brf, arf = setup_prometheus_hook.setup_metrics() 
        before_request_func.extend(brf)
        after_request_func.extend(arf)

        if not apikey_service_host:
            try:
                apikey_service_host =  app.config["application"]["apikey_service_host"]
            except Exception as e:
                logger.error("Failed to start server because no apikey service host provide") 

        apikey_tracking_func = partial(request, apikey_tracking, service_name, apikey_service_host)
        after_request_func.append(apikey_tracking_func)

        def apply_before_after_request():
            for func in before_request_func:
                app.before_request(func)
            
            for idx in range(len(after_request_func)-1, -1, -1):
                app.after_request(after_request_func[idx])

        apply_before_after_request() 
        
        from .utils.flask.error_handler import error_handler
        app.register_blueprint(error_handler)

        @app.route('/health')
        def health():
            return HttpResonse.success(message="Ok", status_code=200)

        @app.route('/metrics/')
        def metrics():
            return Response(prometheus_client.generate_latest(), mimetype=CONTENT_TYPE_LATEST) 
            
        @app.route("/test-api-signature")
        @api_signature_required(
            private_key_file=app.config["application"]["private_key_file"],
            apikey_service_host=app.config["application"]["apikey_service_host"]
        )
        def test_api_signature():
            return  HttpResonse.success(None, "Ok", 200)

        @app.route("/sign-api-signature", methods=["POST"]) 
        def sign_api_signature():
            apikey = request.headers.get("x-api-key")
            if not apikey:
                return HttpResonse.fail(None, "No api key provided", 403)
            headers = create_sign_header(apikey=apikey)
            return HttpResonse.success(headers, "Sign success!", 200)
