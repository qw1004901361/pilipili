# coding=UTF-8
"""本模块完成权限加载，拦截"""
from functools import wraps

from flask import session, request
from flask_login import current_user, logout_user

from app.libs.error_code import AuthFailed, Forbidden, UserNotFound
from app.models.user import BaseUser, UserRole, RoleAuth, AuthModule


def user_auth(func):
    """权限控制装饰器"""

    @wraps(func)
    def decorator(*args, **kwargs):
        """从session读取当前用户的权限"""
        apis = session.get("api")
        modules = session.get("module")

        if apis == None and modules == None:
            raise AuthFailed()

        allow = is_in_scope(apis, modules, request.endpoint)
        if not allow:
            raise Forbidden()
        return func(*args, **kwargs)

    return decorator


def is_in_scope(api, module, endpoint):
    splits = endpoint.split("+")
    module_name = splits[0]
    api_name = splits[1]
    if api_name in api.keys():
        return True
    if module_name in module.keys():
        return True
    else:
        return False


def load_auth():
    """加载权限"""
    baseuser = BaseUser.query.filter(BaseUser.id == current_user.id).first()
    if not baseuser:
        logout_user()
        raise UserNotFound()
    roles = [i.role_id for i in UserRole.query.filter(UserRole.user_id == baseuser.id).all()]
    # 拥有的权限ID
    modules_id = RoleAuth.query.filter(RoleAuth.role_id.in_(roles)).all()
    # 拥有的权限模块的信息
    modules = AuthModule.query.filter(AuthModule.id.in_([i.auth_id for i in modules_id])).all()

    r = {i.module: i.name for i in modules}

    # 将权限写入session
    session["api"] = {}
    session["module"] = r


def unload_auth():
    """清空session中当前用户的权限"""
    session.pop("api", None)
    session.pop("module", None)
    # session.clear
