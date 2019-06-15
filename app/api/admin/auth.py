# coding=UTF-8
import uuid

from flasgger import swag_from
from flask import current_app
from flask_login import login_required, current_user
from sqlalchemy import or_

from app.forms.auth import AuthModuleForm, AuthModuleEditForm, AuthApiEditForm, AuthApiForm
from app.forms.other import PageForm, IdForm, SearchForm
from app.libs.auth import user_auth
from app.libs.enums import ReturnEnum
from app.libs.redprint import Redprint
from app.libs.utils import logging, write_oplog
from app.models.base import db
from app.models.user import AuthModule, AuthApi, UserRole, RoleAuth
from app.view_models.return_obj import ReturnObj

"""
权限模块（超级管理员）
添加权限模块
列出权限模块
删除权限模块
编辑权限模块
查询权限模块
添加权限接口
列出权限接口
删除权限接口
编辑权限接口
查询权限接口
"""

auth = Redprint("auth")


@auth.route("/add_module", methods=["POST"])
@login_required
# @user_auth
@swag_from("../../yml/admin/auth/add_module.yml")
def add_module():
    """添加一个权限模块"""
    form = AuthModuleForm().validate_for_api()
    with db.auto_commit():
        authmodule = AuthModule()
        authmodule.name = form.name.data
        authmodule.module = form.module.data
        db.session.add(authmodule)
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")


@auth.route("/list_module")
@login_required
# @user_auth
@swag_from("../../yml/admin/auth/list_module.yml")
def list_module():
    """列出权限模块"""
    form = PageForm().validate_for_api()
    page_data = AuthModule.query
    if form.q.data:
        page_data = page_data.filter(or_(AuthModule.id == form.q.data, AuthModule.name.like("%" + form.q.data + "%")))
    page_data = page_data.paginate(error_out=False, page=int(form.page.data),
                                   per_page=int(form.pagesize.data))
    modules = []
    for i in page_data.items:
        module = {
            "id": i.id,
            "name": i.name,
            "module": i.module,
            "create_time": i.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        modules.append(module)
    r = {
        "has_next": page_data.has_next,
        "has_prev": page_data.has_prev,
        "pages": page_data.pages,
        "page": page_data.page,
        "total": page_data.total,
        "modules": modules
    }
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@auth.route("/del_module")
@login_required
# @user_auth
@swag_from("../../yml/admin/auth/del_module.yml")
def del_module():
    """删除权限模块"""
    form = IdForm().validate_for_api()
    authmodule = AuthModule.query.filter(AuthModule.id == form.id.data). \
        first_or_404("找不到该权限模块")
    with db.auto_commit():
        # 先删除该模块的下所有接口
        for i in AuthApi.query.filter(AuthApi.module_id == authmodule.id).all():
            db.session.delete(i)
        # 再删除该模块
        db.session.delete(authmodule)
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")


@auth.route("/edit_module", methods=["POST"])
@login_required
# @user_auth
@swag_from("../../yml/admin/auth/edit_module.yml")
def edit_module():
    """编辑权限模块"""
    form = AuthModuleEditForm().validate_for_api()
    authmodule = form.obj
    with db.auto_commit():
        if form.module.data:
            authmodule.module = form.module.data
        if form.name.data:
            authmodule.name = form.name.data
        db.session.add(authmodule)
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")


# @auth.route("/view_module", methods=["GET", "POST"])
# @login_required
# @user_auth
# def view_module():
#     """查找（名字或ID）权限模块"""
#     form = SearchForm().validate_for_api()
#     q = form.q.data
#     try:
#         uuid.UUID(form.q.data)
#         authmodule = AuthModule.query.filter(AuthModule.auth_module_id == q).first()
#         r = {
#             "next_num": None,
#             "has_next": False,
#             "has_prev": False,
#             "modules": [{
#                 "auth_module_id": authmodule.auth_module_id,
#                 "name": authmodule.module_name,
#                 "module": authmodule.auth_module,
#                 "create_time": authmodule.create_time}],
#             "total": 1 if authmodule else 0
#         }
#         logging()
#         return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "查询权限模块成功", data=r)
#     except ValueError:
#         pass
#     page_data = AuthModule.query.filter(AuthModule.module_name.like("%" + q + "%")). \
#         paginate(error_out=False, page=int(form.page.data), per_page=int(current_app.config["ADMIN_PER_MODULE_PAGE"]))
#     r = {
#         "next_num": page_data.next_num,
#         "has_next": page_data.has_next,
#         "has_prev": page_data.has_prev,
#         "modules": [{
#             "auth_module_id": i.auth_module_id,
#             "name": i.module_name,
#             "module": i.auth_module,
#             "create_time": i.create_time.strftime("%Y-%m-%d %H:%M:%S")
#         } for i in page_data.items],
#         "total": page_data.total
#     }
#     logging()
#     return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "查询权限模块成功", data=r)


# @auth.route("/add_api", methods=["GET"])
# @login_required
# # @user_auth
# def add_auth_api():
#     """添加权限接口"""
#     form = AuthApiForm().validate_for_api()
#     with db.auto_commit():
#         authapi = AuthApi()
#         authapi.auth_api_id = str(uuid.uuid1())
#         authapi.auth_module_id = form.module_id.data
#         authapi.auth_api = form.api.data
#         authapi.api_name = form.name.data
#         db.session.add(authapi)
#     logging()
#     return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "添加权限接口成功")
#
#
# @auth.route("/list_api", methods=["GET"])
# @login_required
# @user_auth
# def list_auth_api():
#     """列出权限接口"""
#     form = PageForm().validate_for_api()
#     page_data = AuthApi.query.paginate(error_out=False, page=int(form.page.data),
#                                        per_page=int(current_app.config["ADMIN_PER_MODULE_PAGE"]))
#     r = {
#         "next_num": page_data.next_num,
#         "has_next": page_data.has_next,
#         "has_prev": page_data.has_prev,
#         "apis": [{
#             "auth_api_id": i.auth_api_id,
#             "name": i.api_name,
#             "api": i.auth_api,
#             "module_name":
#                 AuthModule.query.filter(AuthModule.auth_module_id == i.auth_module_id).first().module_name,
#             "create_time": i.create_time.strftime("%Y-%m-%d %H:%M:%S")
#         } for i in page_data.items],
#         "total": page_data.total
#     }
#     logging()
#     return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "列出权限模块成功", data=r)
#
#
# @auth.route("/del_api", methods=["GET"])
# @login_required
# @user_auth
# def del_auth_api():
#     """删除权限接口"""
#     form = IdForm().validate_for_api()
#     authapi = AuthApi.query.filter(AuthApi.auth_api == form.id.data). \
#         first_or_404(description="找不到权限接口")
#     with db.auto_commit():
#         db.session.delete(authapi)
#     logging()
#     return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "删除权限接口成功")
#
#
# @auth.route("/edit_api", methods=["GET", "POST"])
# @login_required
# @user_auth
# def edit_auth_api():
#     """编辑权限接口"""
#     form = AuthApiEditForm().validate_for_api()
#     authapi = form.obj
#     with db.auto_commit():
#         if form.module_id.data:
#             authapi.auth_module_id = form.module_id.data
#         if form.api.data:
#             authapi.auth_api = form.api.data
#         if form.name.data:
#             authapi.api_name = form.name.data
#         db.session.add(authapi)
#     logging()
#     return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "编辑权限接口成功")
#
#
# @auth.route("/view_api", methods=["GET", "POST"])
# @login_required
# @user_auth
# def view_auth_api():
#     """查询权限接口"""
#     form = SearchForm().validate_for_api()
#     q = form.q.data
#     try:
#         uuid.UUID(form.q.data)
#         authapi = AuthApi.query.filter(AuthApi.auth_api_id == q).first()
#         r = {
#             "next_num": None,
#             "has_next": False,
#             "has_prev": False,
#             "apis": [{
#                 "id": authapi.auth_api_id,
#                 "name": authapi.api_name,
#                 "api": authapi.auth_api,
#                 "module_name":
#                     AuthModule.query.filter(
#                         AuthModule.auth_module_id == authapi.auth_module_id).first().module_name,
#                 "create_time": authapi.create_time}],
#             "total": 1 if authapi else 0
#         }
#         logging()
#         return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "查询权限接口成功", data=r)
#     except ValueError:
#         pass
#     # 尝试模糊查询模块权限
#     page_data = AuthApi.query.join(AuthModule, AuthApi.auth_module_id == AuthModule.auth_module_id). \
#         filter(AuthModule.module_name.like("%" + q + "%")). \
#         paginate(error_out=False, page=int(form.page.data), per_page=int(current_app.config["ADMIN_PER_MODULE_PAGE"]))
#     if page_data.total != 0:
#         r = {
#             "next_num": page_data.next_num,
#             "has_next": page_data.has_next,
#             "has_prev": page_data.has_prev,
#             "apis": [{
#                 "id": i.auth_api_id,
#                 "name": i.api_name,
#                 "api": i.auth_api,
#                 "module_name":
#                     AuthModule.query.filter(AuthModule.auth_module_id == i.auth_module_id).first().module_name,
#                 "create_time": i.create_time.strftime("%Y-%m-%d %H:%M:%S")
#             } for i in page_data.items],
#             "total": page_data.total
#         }
#         logging()
#         return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "查询权限接口成功", data=r)
#     # 尝试模糊查询模块接口
#     page_data = AuthApi.query.filter(AuthApi.api_name.like("%" + q + "%")). \
#         paginate(error_out=False, page=int(form.page.data), per_page=int(current_app.config["ADMIN_PER_MODULE_PAGE"]))
#     r = {
#         "next_num": page_data.next_num,
#         "has_next": page_data.has_next,
#         "has_prev": page_data.has_prev,
#         "apis": [{
#             "id": i.auth_api_id,
#             "name": i.api_name,
#             "api": i.auth_api,
#             "module_name":
#                 AuthModule.query.filter(AuthModule.auth_module_id == i.auth_module_id).first().module_name,
#             "create_time": i.create_time.strftime("%Y-%m-%d %H:%M:%S")
#         } for i in page_data.items],
#         "total": page_data.total
#     }
#     logging()
#     return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "查询权限接口成功", data=r)
