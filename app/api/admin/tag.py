# coding=UTF-8
from flasgger import swag_from
from flask import current_app
from flask_login import login_required
from sqlalchemy import or_

from app.forms.other import TagAddForm, TagEditForm, TagListForm, IdForm, SearchForm
from app.libs.auth import user_auth
from app.libs.enums import ReturnEnum
from app.libs.redprint import Redprint
from app.libs.utils import write_oplog
from app.models.base import db
from app.models.video import Tag
from app.view_models.return_obj import ReturnObj

"""
视频标签模块（视频管理员，超级管理员）
添加标签
编辑标签
列出标签
删除标签
查找标签
"""

tag = Redprint("tag")


@tag.route("/add", methods=["POST"])
@login_required
# @user_auth
@swag_from("../../yml/admin/tag/add_tag.yml")
def add_tag():
    form = TagAddForm().validate_for_api()
    with db.auto_commit():
        tag = Tag()
        if form.parent_id.data:
            tag.parent_id = form.parent_id.data
        tag.name = form.name.data
        tag.info = form.info.data
        db.session.add(tag)
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")


@tag.route("/edit", methods=["POST"])
# @login_required
# @user_auth
@swag_from("../../yml/admin/tag/edit_tag.yml")
def edit_tag():
    form = TagEditForm().validate_for_api()
    tag = form.obj
    with db.auto_commit():
        if form.parent_id.data:
            tag.parent_id = form.parent_id.data
        if form.name.data:
            tag.name = form.name.data
        if form.info.data:
            tag.info = form.info.data
        db.session.add(tag)
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")


@tag.route("/list")
@login_required
# @user_auth
@swag_from("../../yml/admin/tag/list_tag.yml")
def list_tag():
    form = TagListForm().validate_for_api()
    page_data = Tag.query.filter(Tag.parent_id == 0). \
        paginate(error_out=False,page=int(form.page.data), per_page=int(current_app.config["ADMIN_PER_TAG_PAGE"]))
    tags = []
    for i in page_data.items:
        sub_tags = Tag.query.filter(Tag.parent_id == i.id).all()
        subs = []
        for j in sub_tags:
            sub = {
                "id": j.id,
                "name": j.name,
                "info": j.info,
                "create_time": j.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            subs.append(sub)
        tag = {
            "id": i.id,
            "name": i.name,
            "info": i.info,
            "sub_tags": subs,
            "create_time": i.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "total": len(sub_tags)
        }
        tags.append(tag)
    r = {
        "next_num": page_data.next_num,
        "has_next": page_data.has_next,
        "has_prev": page_data.has_prev,
        "tags": tags,
        "total": page_data.total
    }
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@tag.route("/del")
@login_required
@swag_from("../../yml/admin/tag/del_tag.yml")
def del_tag():
    form = IdForm().validate_for_api()
    tag = Tag.query.filter(Tag.id == form.id.data).first_or_404("找不到该标签")
    with db.auto_commit():
        db.session.delete(tag)
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")


@tag.route("/view")
@login_required
@swag_from("../../yml/admin/tag/view_tag.yml")
def view_tag():
    """通过标签ID或名字查找"""
    form = SearchForm().validate_for_api()
    q = form.q.data
    page_data = Tag.query.filter(Tag.parent_id != None, or_(Tag.name.like("%" + q + "%"), Tag.id == q)). \
        paginate(error_out=False,page=int(form.page.data), per_page=int(current_app.config["ADMIN_PER_TAG_PAGE"]))
    tags = []
    for i in page_data.items:
        sub_tags = Tag.query.filter(Tag.parent_id == i.id).all()
        subs = []
        for j in sub_tags:
            sub = {
                "id": j.id,
                "name": j.name,
                "info": j.info,
                "create_time": j.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            subs.append(sub)
        tag = {
            "id": i.id,
            "name": i.name,
            "info": i.info,
            "sub_tags": subs,
            "create_time": i.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "total": len(sub_tags)
        }
        tags.append(tag)
    r = {
        "next_num": page_data.next_num,
        "has_next": page_data.has_next,
        "has_prev": page_data.has_prev,
        "tags": tags,
        "total": page_data.total
    }
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)

# @tag.route("/get_all")
# @login_required
# # @swag_from("../../yml/admin/tag/tag_add.yml")
# def get_all():
#     """获取所有标签"""
#     tags = Tag.query.filter(Tag.parent_id == 0).all()
#     main = []
#     for i in tags:
#         sub_tags = Tag.query.filter(Tag.parent_id == i.id).all()
#         sub = []
#         for j in sub_tags:
#             sub_tag = {
#                 "id": j.id,
#                 "name": j.name,
#                 "info": j.info
#             }
#             sub.append(sub_tag)
#         main_tag = {
#             "id": i.id,
#             "name": i.name,
#             "sub_tags": sub,
#             "total": len(sub_tags)
#         }
#         main.append(main_tag)
#     r = {
#         "total": len(tags),
#         "tags": main
#     }
#     return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)
