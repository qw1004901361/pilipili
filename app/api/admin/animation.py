# coding=UTF-8
import os
import uuid
from urllib.parse import urljoin

from flasgger import swag_from
from flask import Blueprint, render_template, redirect, url_for, current_app, request
from flask_login import login_required
from sqlalchemy import or_
from werkzeug.utils import secure_filename

from app.forms.other import PageForm, IdForm, SearchForm, AnimationEditForm, AnimationAddForm, AnimationListForm
from app.libs.auth import user_auth
from app.libs.enums import ReturnEnum
from app.libs.redprint import Redprint
from app.libs.utils import logging, change_filename, allowed_image_file, write_oplog
from app.models.base import db
from app.models.video import Animation, Tag
from app.view_models.return_obj import ReturnObj

"""
轮播图模块（视频管理员，超级管理员）
添加轮播图
列出轮播图
删除轮播图
编辑轮播图
"""

animation = Redprint("animation")


@animation.route("/add", methods=["POST"])
@login_required
@user_auth
@swag_from("../../yml/admin/animation/add_animation.yml", methods=['POST'])
def add_animation():
    """添加轮播图"""
    form = AnimationAddForm().validate_for_api()
    with db.auto_commit():
        animation = Animation()
        animation.name = form.name.data
        try:
            file = request.files[form.logo.name]
            if not allowed_image_file(file.filename):
                return ReturnObj.get_response(ReturnEnum.IMAGE_TYPE_ERROR.value, "只允许上传png jpg jpeg gif格式")
            file_logo = secure_filename(file.filename)
            logo = change_filename(file_logo)
            file.save(os.path.join(current_app.config["LOGO_DIR"], logo))
            animation.logo = urljoin(current_app.config["LOGO_PATH"], logo)
        except Exception as e:
            return ReturnObj.get_response(ReturnEnum.UPLOAD_ANIMATION_LOGO.value, "请上传轮播图封面")
        animation.url = form.url.data
        animation.tag_id = form.tag_id.data
        db.session.add(animation)
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")


@animation.route("/list")
@login_required
@user_auth
@swag_from("../../yml/admin/animation/list_animation.yml")
def list_animation():
    """列出轮播图"""
    form = PageForm().validate_for_api()
    page_data = Animation.query
    if form.tag_id.data == -1:
        pass
    else:
        page_data = page_data.filter(Animation.tag_id == form.tag_id.data)
    if form.q.data:
        page_data = page_data.filter(or_(Animation.id == form.q.data, Animation.name.like("%" + form.q.data + "%")))
    page_data = page_data.order_by(Animation.create_time.desc()). \
        paginate(error_out=False, page=int(form.page.data), per_page=int(form.pagesize.data))
    animations = []
    for i in page_data.items:
        tag = Tag.query.filter(Tag.id == i.tag_id).first()
        animation = {
            "id": i.id,
            "tag": tag.name if tag else "未知",
            "name": i.name,
            "logo": i.logo,
            "url": i.url
        }
        animations.append(animation)
    r = {
        "has_next": page_data.has_next,
        "has_prev": page_data.has_prev,
        "pages": page_data.pages,
        "page": page_data.page,
        "total": page_data.total,
        "animations": animations
    }
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@animation.route("/del")
@login_required
@user_auth
@swag_from("../../yml/admin/animation/del_animation.yml")
def del_animation():
    """删除轮播图"""
    form = IdForm().validate_for_api()
    animation = Animation.query.get_or_404(form.id.data, "找不到该轮播图")
    with db.auto_commit():
        db.session.delete(animation)
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")


@animation.route("/edit", methods=["POST"])
@login_required
@user_auth
@swag_from("../../yml/admin/animation/edit_animation.yml")
def edit_animation():
    """编辑轮播图"""
    form = AnimationEditForm().validate_for_api()
    animation = form.obj
    with db.auto_commit():
        if form.name.data:
            animation.name = form.name.data
        try:
            file = request.files[form.logo.name]
            if not allowed_image_file(file.filename):
                return ReturnObj.get_response(ReturnEnum.IMAGE_TYPE_ERROR.value, "只允许上传png jpg jpeg gif格式")
            file_logo = secure_filename(file.filename)
            logo = change_filename(file_logo)
            file.save(os.path.join(current_app.config["LOGO_DIR"], logo))
            animation.logo = urljoin(current_app.config["LOGO_PATH"], logo)
        except Exception as e:
            pass
        if form.url.data:
            animation.url = form.url.data
        if form.tag_id.data:
            animation.tag_id = form.tag_id.data
        db.session.add(animation)
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")
