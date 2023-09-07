from flask import Blueprint
from .http_scheme import HttpResonse

error_handler = Blueprint("errorHandler", __name__)

@error_handler.app_errorhandler(400)
def bad_request_handler(e):
    return HttpResonse.fail(message=e.description, status_code=e.code)