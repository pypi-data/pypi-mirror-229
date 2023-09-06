import pytest
import datetime
from ai_service_wrapper.apisignature.endecrypt import *
from ai_service_wrapper.apisignature.sign import *
from ai_service_wrapper.apisignature.verify import *
from config import config

private_key_file=config["application"]["private_key_file"]
apikey_service_host=config["application"]["apikey_service_host"]

@pytest.fixture()
def valid_http_headers():
    return create_sign_header("sk-oDgBTl8YM4KvpT2iqG3bCTa7KXzc0LwQh08vDz8h4prXvVFNcC")


def test_verify_header(valid_http_headers):
    status, message = verify_header(valid_http_headers,
                                    private_key_file=private_key_file,
                                    apikey_service_host=apikey_service_host)
    assert status is True
    assert message == "Success verify"


def test_apikey_failed_verify_header():
    failed_header = create_sign_header("FailedApiKey")
    status, message = verify_header(failed_header,
                                    private_key_file=private_key_file,
                                    apikey_service_host=apikey_service_host)
    assert status is False
    assert message == "Failed verify apikey"


def test_invalid_timestamp_verify_header():
    datetype_timestamp = datetime.datetime.now
    apikey = "U5NyoG0T4KGlIdd1G25ENg"
    headers = {
        "x-api-key": apikey,
        "x-api-timestamp": datetype_timestamp,
        "x-api-signature": sign(datetype_timestamp, apikey)
    }

    status, message = verify_header(headers, 
                                    private_key_file=private_key_file,
                                    apikey_service_host=apikey_service_host)
    assert status is False
    assert "Timestamp value is not valid type. Must be (float " in message


def test_not_enough_required_header_verify_header():

    headers = {
        "x-api-timestamp": "smth",
        "x-api-signature": "smth"
    }

    status, message = verify_header(headers,
                                    private_key_file=private_key_file,
                                    apikey_service_host=apikey_service_host)
    assert status is False
    assert message == "Headers does not included required param"
