from flask import jsonify

class HttpResonse:
    
    @staticmethod
    def success(data=None, message=None, status_code=None):
        resObj = {
            "data": data,
            "message": message,
            "status": status_code
        }

        return jsonify(resObj), status_code 

    @staticmethod
    def fail(data=None, message=None, status_code=None):
        status = status_code if status_code else 500 
        resObj = {
            "data": data,
            "message": message,
            "status": status
        }

        return jsonify(resObj), status 