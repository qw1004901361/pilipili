# coding=UTF-8
from flasgger import swag_from
from flask import current_app
from flask_login import login_required

from app.forms.other import PageForm, SearchOpLogForm, ListLoginLogForm, SearchLoginLogForm, \
    SearchViewLogForm
from app.libs.auth import user_auth
from app.libs.enums import ReturnEnum
from app.libs.redprint import Redprint
from app.libs.utils import logging, write_oplog
from app.models.log import OpLog, LoginLog, ViewLog

from app.models.user import Admin, User, BaseUser
from app.models.video import Video
from app.view_models.return_obj import ReturnObj

"""
日志模块（日志管理员，超级管理员）
列出操作日志
查询操作日志
列出登录日志
查看登录日志
列出观看日志
查看观看日志
"""

log = Redprint("log")


@log.route("/list_oplog")
@login_required
# @user_auth
@swag_from("../../yml/admin/log/list_oplog.yml")
def list_oplog():
    """列出操作日志"""
    form = PageForm().validate_for_api()
    page_data = OpLog.query.order_by(OpLog.create_time.desc()). \
        paginate(error_out=False,page=int(form.page.data), per_page=int(current_app.config["ADMIN_PER_LOG_PAGE"]))
    logs = []
    for i in page_data.items:
        baseuser = BaseUser.query.filter(BaseUser.id == i.admin_id).first()
        log = {
            "id": i.id,
            "admin": {
                "id": baseuser.id if baseuser else "未知",
                "name": baseuser.name if baseuser else "未知"
            },
            "ip": i.ip,
            "reason": i.reason,
            "create_time": i.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        logs.append(log)
    r = {
        "has_next": page_data.has_next,
        "has_prev": page_data.has_prev,
        "pages": page_data.pages,
        "page": page_data.page,
        "total": page_data.total,
        "logs": logs
    }
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@log.route("/view_oplog")
@login_required
# @user_auth
@swag_from("../../yml/admin/log/view_oplog.yml")
def view_oplog():
    """查询（根据管理员名字或者时间）操作日志"""
    form = SearchOpLogForm().validate_for_api()
    select = OpLog.query.join(BaseUser, BaseUser.id == OpLog.admin_id)
    if form.name.data:
        select = select.filter(BaseUser.name.like("%" + form.name.data + "%"))
    if form.start_date.data:
        select = select.filter(OpLog.create_time.between(
            form.start_date.data, form.end_date.data
        ))
    page_data = select.order_by(OpLog.create_time.desc()). \
        paginate(error_out=False,page=int(form.page.data), per_page=int(current_app.config["ADMIN_PER_LOG_PAGE"]))
    logs = []
    for i in page_data.items:
        baseuser = BaseUser.query.filter(BaseUser.id == i.admin_id).first()
        log = {
            "id": i.id,
            "admin": {
                "id": baseuser.id if baseuser else "未知",
                "name": baseuser.name if baseuser else "未知"
            },
            "ip": i.ip,
            "reason": i.reason,
            "create_time": i.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        logs.append(log)
    r = {
        "has_next": page_data.has_next,
        "has_prev": page_data.has_prev,
        "pages": page_data.pages,
        "page": page_data.page,
        "total": page_data.total,
        "logs": logs
    }
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@log.route("/list_loginlog")
@login_required
# @user_auth
@swag_from("../../yml/admin/log/list_loginlog.yml")
def list_loginlog():
    """列出（可选全部、管理员、普通用户）登录日志"""
    form = ListLoginLogForm().validate_for_api()
    select = LoginLog.query
    if form.tag_id.data == -1:
        pass
    elif form.tag_id.data == 0:
        select = select.join(User, User.id == LoginLog.user_id)
    elif form.tag_id.data == 1:
        select = select.join(Admin, Admin.id == LoginLog.user_id)
    page_data = select.order_by(LoginLog.create_time.desc()). \
        paginate(error_out=False,page=int(form.page.data), per_page=int(current_app.config["ADMIN_PER_LOG_PAGE"]))
    loginlogs = []
    for i in page_data.items:
        baseuser = BaseUser.query.filter(BaseUser.baseuser_id == i.admin_id).first()
        one = {
            "id": i.id,
            "user": {
                "id": baseuser.id if baseuser else "未知",
                "name": baseuser.name if baseuser else "未知",
            },
            "ip": i.ip,
            "create_time": i.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        loginlogs.append(one)
    r = {
        "has_next": page_data.has_next,
        "has_prev": page_data.has_prev,
        "pages": page_data.pages,
        "page": page_data.page,
        "total": page_data.total,
        "loginlogs": loginlogs
    }
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@log.route("/view_loginlog")
@login_required
# @user_auth
@swag_from("../../yml/admin/log/view_loginlog.yml")
def view_loginlog():
    """根据名字查询（可选全部、管理员、普通用户）登录日志"""
    form = SearchLoginLogForm().validate_for_api()
    select = LoginLog.query
    if form.tag_id.data == -1:
        pass
    elif form.tag_id.data == 0:
        select = select.join(User, User.id == LoginLog.user_id)
    elif form.tag_id.data == 1:
        select = select.join(Admin, Admin.id == LoginLog.user_id)
    if form.start_date.data:
        select = select.filter(OpLog.create_time.between(
            form.start_date.data, form.end_date.data))
    page_data = select.filter(BaseUser.name.like("%" + form.name.data + "%")).order_by(
        LoginLog.create_time.desc()). \
        paginate(error_out=False,page=int(form.page.data), per_page=int(current_app.config["ADMIN_PER_LOG_PAGE"]))
    loginlogs = []
    for i in page_data.items:
        baseuser = BaseUser.query.filter(BaseUser.baseuser_id == i.admin_id).first()
        one = {
            "id": i.id,
            "user": {
                "id": baseuser.id if baseuser else "未知",
                "name": baseuser.name if baseuser else "未知",
            },
            "ip": i.ip,
            "create_time": i.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        loginlogs.append(one)
    r = {
        "has_next": page_data.has_next,
        "has_prev": page_data.has_prev,
        "pages": page_data.pages,
        "page": page_data.page,
        "total": page_data.total,
        "loginlogs": loginlogs
    }
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@log.route("/list_viewlog")
@login_required
# @user_auth
@swag_from("../../yml/admin/log/list_viewlog.yml")
def list_viewlog():
    """列出用户观看日志"""
    form = PageForm().validate_for_api()
    page_data = ViewLog.query.join(User, User.user_id == ViewLog.user_id).order_by(
        ViewLog.update_time.desc()). \
        paginate(error_out=False,page=int(form.page.data), per_page=int(current_app.config["ADMIN_PER_LOG_PAGE"]))
    viewlogs = []
    for i in page_data.items:
        baseuser = BaseUser.query.filter(BaseUser.id == i.user_id).first()
        video = Video.query.filter(Video.id == i.video_id).first()
        one = {
            "id": i.id,
            "user": {
                "id": baseuser.id if baseuser else "未知",
                "name": baseuser.name if baseuser else "未知",
            },
            "video": {
                "id": video.id if video else "未知",
                "name": video.name if video else "未知",
            },
            "update_time": i.update_time
        }
        viewlogs.append(one)
    r = {
        "has_next": page_data.has_next,
        "has_prev": page_data.has_prev,
        "pages": page_data.pages,
        "page": page_data.page,
        "total": page_data.total,
        "viewlogs": viewlogs
    }
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@log.route("/view_viewlog")
@login_required
# @user_auth
@swag_from("../../yml/admin/log/view_viewlog.yml")
def view_viewlog():
    """查看用户观看日志"""
    form = SearchViewLogForm().validate_for_api()
    select = ViewLog.query
    if form.start_date.data:
        select = select.filter(ViewLog.update_time.between(form.start_date.data, form.end_date.data))
    select = select.join(BaseUser, BaseUser.id == ViewLog.user_id). \
        filter(BaseUser.name.like("%" + form.name.data + "%")).order_by(
        ViewLog.create_time.desc())
    page_data = select.paginate(error_out=False,page=int(form.page.data), per_page=int(current_app.config["ADMIN_PER_LOG_PAGE"]))
    viewlogs = []
    for i in page_data.items:
        baseuser = BaseUser.query.filter(BaseUser.id == i.user_id).first()
        video = Video.query.filter(Video.id == i.video_id).first()
        one = {
            "id": i.id,
            "user": {
                "id": baseuser.id if baseuser else "未知",
                "name": baseuser.name if baseuser else "未知",
            },
            "video": {
                "id": video.id if video else "未知",
                "name": video.name if video else "未知",
            },
            "update_time": i.update_time
        }
        viewlogs.append(one)
    r = {
        "has_next": page_data.has_next,
        "has_prev": page_data.has_prev,
        "pages": page_data.pages,
        "page": page_data.page,
        "total": page_data.total,
        "viewlogs": viewlogs
    }
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)
