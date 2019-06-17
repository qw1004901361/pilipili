# coding=UTF-8
from app.libs.enums import ReturnEnum
from app.libs.error import APIException


class Success(APIException):
    code = 200
    msg = "success"
    error_code = 0


class DeleteSuccess(Success):
    code = 200
    error_code = -1


class ServerError(APIException):
    code = 200
    msg = "sorry, we make a mistake"
    error_code = 999


class ClientTypeError(APIException):
    # 400参数错误 401未授权 403禁止访问 404未找到资源
    # 500服务器产生未知错误
    # 200查询成功 201创建或更新成功 204删除成功
    # 301 302
    code = 200
    msg = "client is invalid"
    error_code = 1006


class ConnectError(APIException):
    code = 200
    msg = "连接小程序服务器失败"
    error_code = 10007


class AccessError(APIException):
    code = 200
    msg = "获取openid和session_key失败"
    error_code = 10007


class ParameterException(APIException):
    code = 200
    msg = "invalid parameter"
    error_code = ReturnEnum.WTFORMS_FAIL.value


class NotFound(APIException):
    code = 200
    msg = "the resource are not found"
    error_code = ReturnEnum.NOT_FOUND.value


class AuthFailed(APIException):
    # 401代表授权失败
    code = 200
    error_code = 1005
    msg = '加载权限失败'


class Forbidden(APIException):
    # 403代表权限不够，禁止访问
    code = 200
    error_code = 1004
    msg = "没有权限访问"


class DuplicateGift(APIException):
    code = 200
    error_code = 2001
    msg = 'the current book has already in gift'


class TokenError(APIException):
    code = 200
    msg = "token 异常"
    error_code = 1000


class UserNotFound(APIException):
    code = 200
    msg = "找不到该用户"
    error_code = 1000
