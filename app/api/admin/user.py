# coding=UTF-8
import os
import uuid
from urllib.parse import urljoin

from flasgger import swag_from
from flask import Blueprint, render_template, redirect, url_for, current_app, request
from flask_login import login_required
from sqlalchemy import or_
from werkzeug.exceptions import BadRequestKeyError
from werkzeug.utils import secure_filename

from app.forms.other import PageForm, IdForm, SearchForm
from app.forms.user import UserAddForm, UserEditForm, AdminAddUserForm, AdminEditUserForm
from app.libs.auth import user_auth
from app.libs.enums import ReturnEnum
from app.libs.redprint import Redprint
from app.libs.utils import logging, change_filename, allowed_image_file, write_oplog
from app.models.base import db
from app.models.user import User, BaseUser, UserRole, Role, Admin
from app.view_models.return_obj import ReturnObj

"""
管理用户模块（用户管理员，超级管理员）
列出用户
删除用户
添加用户
编辑用户
"""

user = Redprint("user")


@user.route("/list")
@login_required
@swag_from("../../yml/admin/user/list_user.yml")
# @user_auth
def list_user():
    """列出用户"""
    form = PageForm().validate_for_api()
    page_data = BaseUser.query
    if form.q.data:
        page_data = page_data.join(User, BaseUser.id == User.id). \
            filter(or_(BaseUser.id == form.q.data, BaseUser.name.like("%" + form.q.data + "%")))
    page_data = page_data.order_by(BaseUser.create_time.desc()). \
        paginate(error_out=False, page=int(form.page.data), per_page=int(form.pagesize.data))
    users = []
    for i in page_data.items:
        user = User.query.filter(User.id == i.id).first()
        one = {
            "id": i.id,
            "name": i.name,
            "account": i.account,
            "gender": i.gender,
            "email": user.email if user else None,
            "phone": user.phone if user else None,
            "info": user.info if user else None,
            "face": user.face if user else None,
            "create_time": i.create_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        users.append(one)
    r = {
        "has_next": page_data.has_next,
        "has_prev": page_data.has_prev,
        "pages": page_data.pages,
        "page": page_data.page,
        "total": page_data.total,
        "users": users
    }
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@user.route("/del", methods=["GET"])
@login_required
@swag_from("../../yml/admin/user/del_user.yml")
# @user_auth
def del_user():
    """删除用户"""
    form = IdForm().validate_for_api()
    user = User.query.get_or_404(form.id.data, "找不到该用户")
    admin = Admin.query.filter(Admin.id == user.id).first()
    if admin:
        return ReturnObj.get_response(ReturnEnum.ADMIN_DEL_ERROR.value, "该用户也是管理员，不能删除")
    with db.auto_commit():
        # 删除用户的角色关联
        user_role = UserRole.query.filter(UserRole.user_id == user.id).all()
        for i in user_role:
            db.session.delete(i)
        # 删除用户额外信息
        db.session.delete(user)
        # 删除用户基本信息
        baseuser = BaseUser.query.filter(BaseUser.id == user.id).first()
        db.session.delete(baseuser)
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")


@user.route("/add", methods=["POST"])
@login_required
# @user_auth
@swag_from("../../yml/admin/user/add_user.yml")
def add_user():
    """添加用户"""
    form = AdminAddUserForm().validate_for_api()
    baseuser = register_user(form)
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data={"id": baseuser.id})


@user.route("/edit", methods=["POST"])
@login_required
@swag_from("../../yml/admin/user/edit_user.yml")
# @user_auth
def edit_user():
    """编辑用户"""
    form = AdminEditUserForm().validate_for_api()
    baseuser = form.obj
    user = User.query.filter(User.id == baseuser.id).first()
    try:
        if form.name.data:
            baseuser.name = form.name.data
        if form.gender.data:
            baseuser.gender = form.gender.data
        if form.pwd.data:
            baseuser.pwd = form.pwd.data
        db.session.add(baseuser)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
    try:
        if form.email.data:
            user.email = form.email.data
        if form.phone.data:
            user.phone = form.phone.data
        if form.info.data:
            user.info = form.info.data
        try:
            file = request.files[form.face.name]
            if not allowed_image_file(file.filename):
                return ReturnObj.get_response(ReturnEnum.IMAGE_TYPE_ERROR.value, "只允许上传png jpg jpeg gif格式")
            file_face = secure_filename(file.filename)
            face = change_filename(file_face)
            file.save(os.path.join(current_app.config["FACE_DIR"], face))
            user.face = urljoin(current_app.config["FACE_PATH"], face)
        except BadRequestKeyError as e:
            pass
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data={"id": baseuser.id})


def register_user(form):
    """添加普通用户"""
    try:
        # 基本用户
        baseuser = BaseUser()
        baseuser.account = form.account.data
        baseuser.pwd = form.pwd.data
        baseuser.name = form.name.data
        baseuser.gender = form.gender.data
        db.session.add(baseuser)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        return ReturnObj.get_response(ReturnEnum.ADD_BASEUSER_FAIL.value, "添加用户基本信息失败")
    baseuser = BaseUser.query.filter(BaseUser.account == form.account.data).first()
    try:
        # 用户其他信息
        user = User()
        user.id = baseuser.id
        if form.phone.data:
            user.phone = form.phone.data
        if form.email.data:
            user.email = form.email.data
        if form.info.data:
            user.info = form.info.data
        try:
            file = request.files[form.face.name]
            if not allowed_image_file(file.filename):
                return ReturnObj.get_response(ReturnEnum.IMAGE_TYPE_ERROR.value, "只允许上传png jpg jpeg gif格式")
            file_face = secure_filename(file.filename)
            face = change_filename(file_face)
            file.save(os.path.join(current_app.config["FACE_DIR"], face))
            user.face = urljoin(current_app.config["FACE_PATH"], face)
        except BadRequestKeyError as e:
            pass
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        return ReturnObj.get_response(ReturnEnum.ADD_USER_FAIL.value, "添加用户额外信息失败")
    try:
        user_role = UserRole()
        user_role.user_id = baseuser.id
        user_role.role_id = Role.query.filter(Role.name == "普通用户").first().id
        db.session.add(user_role)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        return ReturnObj.get_response(ReturnEnum.ADD_USERROLE_FAIL.value, "赋予用户角色失败")
    return baseuser
