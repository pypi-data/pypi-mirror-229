import functools

from flask import request
from werkzeug.exceptions import BadRequest
from ai_service_wrapper.utils.fastapi.exceptions import BadRequestException

from .verify import verify_header

def flask_api_signature_required(private_key_file, apikey_service_host):
    def wrapped_func(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            access_control_request_headers = request.headers.get(
                "access-control-request-headers")
            if request.method == "OPTIONS" and access_control_request_headers:
                has_access_control = map(lambda value: value.lower(), 
                                    access_control_request_headers.split(",").
                                    index('x-api-signature'))
            else:
                has_access_control = False

            if not has_access_control:    

                status, message = verify_header(
                    headers=request.headers, 
                    private_key_file=private_key_file,
                    apikey_service_host=apikey_service_host,
                    request_lifetime=3000,
                )
            
                if not status:
                    raise BadRequest(description=message)
            return view(**kwargs)
        return wrapped_view

    return wrapped_func

def fast_api_signature_required(private_key_file, apikey_service_host):
    def wrapped_func(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            request = kwargs.get("request")
            access_control_request_headers = request.headers.get(
                "access-control-request-headers")
            if request.method == "OPTIONS" and access_control_request_headers:
                has_access_control = map(lambda value: value.lower(), 
                                    access_control_request_headers.split(",").
                                    index('x-api-signature'))
            else:
                has_access_control = False

            if not has_access_control:    

                status, message = verify_header(
                    headers=request.headers, 
                    private_key_file=private_key_file,
                    apikey_service_host=apikey_service_host,
                    request_lifetime=3000,
                )

                if not status:
                    raise BadRequestException(detail=message)

            return view(**kwargs)
        return wrapped_view

    return wrapped_func

def async_fast_api_signature_required(private_key_file, 
                                      apikey_service_host, 
                                      request_lifetime=300):
    def wrapped_func(view):
        @functools.wraps(view)
        async def wrapped_view(**kwargs):
            request = kwargs.get("request")
            access_control_request_headers = request.headers.get(
                "access-control-request-headers")
            if request.method == "OPTIONS" and access_control_request_headers:
                has_access_control = map(lambda value: value.lower(), 
                                    access_control_request_headers.split(",").
                                    index('x-api-signature'))
            else:
                has_access_control = False

            if not has_access_control:    

                status, message = verify_header(
                    headers=request.headers, 
                    private_key_file=private_key_file,
                    apikey_service_host=apikey_service_host,
                    request_lifetime=request_lifetime,
                )

                if not status:
                    raise BadRequestException(detail=message)

            return await view(**kwargs)
        return wrapped_view

    return wrapped_func