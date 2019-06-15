# coding=UTF-8
from flask import make_response, jsonify, request


class ReturnObj:

    @classmethod
    def get_response(cls, error_code, msg, data=None, code=200):
        r = {
            "error_code": error_code,
            "msg": msg,
            "data": data,
            "request": request.method + " " + cls._get_url_no_param()
        }
        response = make_response(jsonify(r))
        response.status_code = code
        response.headers["Content-Type"] = "application/json"

        return response

    @classmethod
    def _get_url_no_param(cls):
        full_path = str(request.full_path)
        main_path = full_path.split("?")
        return main_path[0]
