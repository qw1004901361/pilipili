# coding=UTF-8
import uuid

from flasgger import swag_from
from flask import Blueprint, render_template, redirect, url_for, current_app
from flask_login import login_required
from sqlalchemy import or_

from app.forms.auth import RoleAddForm, RoleEditForm
from app.forms.other import IdForm, PageForm, SearchForm
from app.libs.auth import user_auth
from app.libs.enums import ReturnEnum
from app.libs.redprint import Redprint
from app.libs.utils import logging, write_oplog
from app.models.base import db
from app.models.user import Role, AuthModule, UserRole, RoleAuth, BaseUser
from app.view_models.return_obj import ReturnObj

"""
角色模块（超级管理员）
添加角色
编辑角色
列出角色
删除角色
查找角色
"""

role = Redprint("role")


@role.route("/add", methods=["POST"])
@login_required
# @user_auth
@swag_from("../../yml/admin/role/add_role.yml")
def add_role():
    form = RoleAddForm()
    form.auths.choices = [(v.id, v.name) for v in AuthModule.query.all()]
    form.validate_for_api()
    with db.auto_commit():
        # 添加角色
        role = Role(name=form.name.data)
        db.session.add(role)
        # 关联权限
        for i in form.auths.data:
            db.session.add(RoleAuth(role_id=role.id, auth_id=i))
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")


@role.route("/list")
@login_required
# @user_auth
@swag_from("../../yml/admin/role/list_role.yml")
def list_role():
    """列出角色列表，并找出哪些用户拥有该角色"""
    form = PageForm().validate_for_api()
    page_data = Role.query.paginate(page=int(form.page.data), per_page=int(current_app.config["ADMIN_PER_ROLE_PAGE"]))
    roles = []
    for i in page_data.items:
        users = []
        for j in BaseUser.query.join(UserRole, UserRole.user_id == BaseUser.id).filter(UserRole.role_id == i.id).all():
            user = {
                "id": j.id,
                "name": j.name
            }
            users.append(user)
        role = {
            "id": i.id,
            "name": i.name,
            "users": users,
            "create_time": i.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        roles.append(role)
    r = {
        "has_next": page_data.has_next,
        "has_prev": page_data.has_prev,
        "pages": page_data.pages,
        "page": page_data.page,
        "total": page_data.total,
        "roles": roles
    }
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@role.route("/del", methods=["GET"])
@login_required
# @user_auth
@swag_from("../../yml/admin/role/del_role.yml")
def del_role():
    form = IdForm().validate_for_api()
    role = Role.query.filter(Role.id == form.id.data).first_or_404(description="找不到该角色")
    with db.auto_commit():
        # 删除该角色所拥有的权限关联
        for role_auth in RoleAuth.query.filter(RoleAuth.role_id == role.id).all():
            db.session.delete(role_auth)
        # 删除拥有该角色的用户关联
        for user_role in UserRole.query.filter(UserRole.role_id == role.id).all():
            db.session.delete(user_role)
        # 删除该角色
        db.session.delete(role)
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")


@role.route("/edit", methods=["POST"])
@login_required
# @user_auth
@swag_from("../../yml/admin/role/edit_role.yml")
def edit_role():
    form = RoleEditForm()
    form.auths.choices = [(v.id, v.name) for v in AuthModule.query.all()]
    form.validate_for_api()
    role = form.obj
    with db.auto_commit():
        if form.name.data:
            role.name = form.name.data
        db.session.add(role)
        if form.auths.data:
            # 删除原来的权限
            for i in RoleAuth.query.filter(RoleAuth.role_id == role.role_id).all():
                db.session.delete(i)
            # 添加新的权限
            for i in form.auths.data:
                db.session.add(RoleAuth(role_id=role.role_id, auth_id=i))
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")


@role.route("/view")
@login_required
# @user_auth
# @swag_from("../../yml/admin/role/view_role.yml")
def view_role():
    """根据角色ID或者角色名字搜索"""
    form = SearchForm().validate_for_api()
    q = form.q.data
    page_data = Role.query.filter(or_(Role.name.like("%" + q + "%"), Role.id == q)). \
        paginate(page=int(form.page.data), per_page=int(current_app.config["ADMIN_PER_ROLE_PAGE"]))
    roles = []
    for i in page_data.items:
        users = []
        for j in BaseUser.query.join(UserRole, UserRole.user_id == BaseUser.id).filter(UserRole.role_id == i.id).all():
            user = {
                "id": j.id,
                "name": j.name
            }
            users.append(user)
        role = {
            "id": i.id,
            "name": i.name,
            "users": users,
            "create_time": i.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        roles.append(role)
    r = {
        "has_next": page_data.has_next,
        "has_prev": page_data.has_prev,
        "pages": page_data.pages,
        "page": page_data.page,
        "total": page_data.total,
        "roles": roles
    }
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)