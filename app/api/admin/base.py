# coding=UTF-8
import datetime
import os
import uuid

from flasgger import swag_from
from flask import redirect, url_for, request, flash, Blueprint, current_app, session
from flask_login import login_user, logout_user, login_required, current_user

from app.forms.auth import LoginForm, PwdForm
from app.forms.user import AdminEditForm
from app.libs.auth import user_auth, load_auth, unload_auth
from app.libs.enums import ReturnEnum
from app.libs.redprint import Redprint
from app.models.base import db
from app.models.log import LoginLog
from app.models.user import Admin, BaseUser, UserRole, Role, RoleAuth, AuthModule
from app.models.video import Tag

from app.view_models.return_obj import ReturnObj

"""
管理员基本操作
登录
登出
修改密码
修改个人信息
"""

base = Redprint("base")


@base.route("/login", methods=["POST"])
@swag_from("../../yml/admin/base/login.yml")
def login():
    form = LoginForm().validate_for_api()
    baseuser = BaseUser.query.join(Admin).filter(BaseUser.account == form.account.data).first()
    if baseuser and baseuser.check_pwd(form.pwd.data):
        # 第三方插件实现写入cookie
        continued_time = datetime.timedelta(hours=2)  # cookie有效时间
        # 将当前用户的信息写入session
        login_user(baseuser, remember=True, duration=continued_time)
        # 加载当前用户的权限，写入session
        load_auth()
        with db.auto_commit():
            # 管理员登录次数+1
            admin = Admin.query.filter(Admin.id == current_user.id).first_or_404("找不到该管理员")
            admin.login_counter += 1
            # 记录管理员登录记录
            loginlog = LoginLog(user_id=current_user.id, ip=request.remote_addr)
            db.session.add(admin)
            db.session.add(loginlog)
        with db.auto_commit():
            # 记录用户登录记录
            loginlog = LoginLog(user_id=current_user.id, ip=request.remote_addr)
            db.session.add(loginlog)
        roles = [i.name for i in
                 Role.query.join(UserRole, UserRole.role_id == Role.id).filter(UserRole.user_id == admin.id).all()]
        r = {
            "total": len(roles),
            "roles": roles
        }
        return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)
    return ReturnObj.get_response(ReturnEnum.LOGIN_ERROR.value, "帐号不存在或密码错误")


@base.route("/logout")
@login_required
@swag_from("../../yml/admin/base/logout.yml")
def logout():
    # 从session中清除当前用户的信息
    logout_user()
    # 清空session
    # session.clear
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")


@base.route("/pwd", methods=["POST"])
@login_required
@swag_from("../../yml/admin/base/pwd.yml")
def pwd():
    form = PwdForm().validate_for_api()
    baseuser = BaseUser.query.filter(BaseUser.id == current_user.id).first_or_404(description="用户不存在")
    baseuser.pwd = form.new_pwd.data
    with db.auto_commit():
        db.session.add(baseuser)
    logout_user()
    # 清空加载的权限
    unload_auth()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")


@base.route("/edit", methods=["POST"])
@login_required
@swag_from("../../yml/admin/base/edit.yml")
def edit():
    form = AdminEditForm().validate_for_api()
    baseuser = BaseUser.query.filter(BaseUser.id == current_user.id).first_or_404(description="找不到该用户")
    with db.auto_commit():
        if form.name.data:
            baseuser.name = form.name.data
        if form.gender.data:
            baseuser.gender = form.gender.data
        db.session.add(baseuser)
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")


@base.route("/info")
@login_required
@swag_from("../../yml/admin/base/info.yml")
def info():
    """获取当前登录管理员信息"""
    r = {
        "id": current_user.id,
        "name": current_user.name,
        "gender": current_user.gender,
        "account": current_user.account
    }
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@base.route("/get_all_tag")
@login_required
@swag_from("../../yml/admin/base/get_all_tag.yml")
def get_all_tag():
    """获取所有标签"""
    page_data = Tag.query.filter(Tag.parent_id == 0).all()
    tags = []
    for i in page_data:
        sub_page_data = Tag.query.filter(Tag.parent_id == i.id).all()
        sub_tags = []
        for j in sub_page_data:
            sub_tag = {
                "id": j.id,
                "name": j.name,
                "info": j.info
            }
            sub_tags.append(sub_tag)
        tag = {
            "id": i.id,
            "name": i.name,
            "children": sub_tags,
            "total": len(sub_page_data)
        }
        tags.append(tag)
    r = {
        "data": tags,
        "total": len(page_data)
    }
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@base.route("/get_all_role")
@login_required
# @user_auth
@swag_from("../../yml/admin/base/get_all_role.yml")
def get_all_role():
    """获得所有的角色"""
    roles = [{"id": i.id, "name": i.name} for i in Role.query.all()]
    r = {
        "total": len(roles),
        "roles": roles
    }
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@base.route("/get_my_module")
@login_required
# @user_auth
@swag_from("../../yml/admin/base/get_my_module.yml")
def get_my_module():
    """获得自己所拥有的的权限"""
    roles_id = [i.role_id for i in UserRole.query.filter(UserRole.user_id == current_user.id).all()]
    authmodules_id = [i.auth_id for i in RoleAuth.query.filter(RoleAuth.role_id.in_(roles_id)).all()]
    authmodules = AuthModule.query.filter(AuthModule.id.in_(authmodules_id)).all()
    modules = []
    for i in authmodules:
        one = {
            "id": i.id,
            "name": i.name,
            "module": i.module
        }
        modules.append(one)
    r = {
        "total": len(modules),
        "modules": modules
    }
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)
