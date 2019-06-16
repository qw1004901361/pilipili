# coding=UTF-8

from flasgger import swag_from
from flask import current_app
from flask_login import current_user, login_required
from sqlalchemy import or_

from app.forms.other import PageForm, IdForm, SearchForm, ListComForm
from app.libs.auth import user_auth
from app.libs.enums import ReturnEnum
from app.libs.redprint import Redprint
from app.libs.utils import write_oplog
from app.models.base import db
from app.models.video import Comment, Video
from app.models.user import User, BaseUser
from app.view_models.return_obj import ReturnObj

"""
评论模块（视频管理员，超级管理员）
列出评论
删除评论
"""

comment = Redprint("comment")


@comment.route("/list")
@login_required
# @user_auth
@swag_from("../../yml/admin/comment/list_comment.yml")
def list_comment():
    """列出评论"""
    form = ListComForm().validate_for_api()
    page_data = Comment.query
    if form.video_id.data:
        page_data = page_data.filter(Comment.video_id == form.video_id.data)
    if form.q.data:
        page_data = page_data.filter(or_(Video.name.like("%" + form.q.data + "%"),
                                         Comment.id == form.q.data, Comment.content.like("%" + form.q.data + "%")))
    page_data = page_data.order_by(Comment.create_time.desc()). \
        paginate(error_out=False, page=int(form.page.data), per_page=int(form.pagesize.data))
    comments = []
    for i in page_data.items:
        baseuser = BaseUser.query.filter(BaseUser.id == i.user_id).first()
        video = Video.query.filter(Video.id == i.video_id).first()
        comment = {
            "id": i.id,
            "user": {
                "id": baseuser.id if baseuser else "未知",
                "name": baseuser.name if baseuser else "未知",
            },
            "video": {
                "id": video.id if video else "未知",
                "name": video.name if video else "未知",
            },
            "content": i.content,
            "create_time": i.create_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        comments.append(comment)
    r = {
        "has_next": page_data.has_next,
        "has_prev": page_data.has_prev,
        "pages": page_data.pages,
        "page": page_data.page,
        "total": page_data.total,
        "comments": comments
    }
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@comment.route("/del")
@login_required
# @user_auth
@swag_from("../../yml/admin/comment/del_comment.yml")
def del_comment():
    """删除评论"""
    form = IdForm().validate_for_api()
    comment = Comment.query.filter(Comment.id == form.id.data).first_or_404(description="找不到该评论")
    with db.auto_commit():
        db.session.delete(comment)
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")


@comment.route("/del_by_video")
@login_required
@swag_from("../../yml/admin/comment/del_by_video.yml")
def del_by_video():
    """根据视频id删除该视频的所有评论"""
    form = IdForm().validate_for_api()
    comments = Comment.query.filter(Comment.video_id == form.id.data).all()
    with db.auto_commit():
        for i in comments:
            db.session.delete(i)
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")
