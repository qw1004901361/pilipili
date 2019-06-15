# coding=UTF-8
from flask import current_app, jsonify
from flask_login import login_required, current_user

from app.forms.other import PageForm, ListComForm, LoadComForm, CommentAddForm, IdForm
from app.libs.auth import user_auth
from app.libs.enums import ReturnEnum
from app.libs.redprint import Redprint
from app.libs.utils import logging, num_assign
from app.models.video import Comment, Video
from app.models.user import BaseUser, User, Follow
from app.view_models.return_obj import ReturnObj
from app.models.base import db

comment = Redprint("comment")

"""
评论
加载评论
"""


@comment.route("/list")
def list_comment():
    form = ListComForm().validate_for_api()
    page_data = Comment.query
    if form.start_time.data and form.end_time.data:
        page_data = page_data.filter(Comment.create_time.between(form.start_time.data, form.end_time.data))
    if form.order_by.data == "desc":
        page_data = page_data.order_by(Comment.create_time.desc())
    else:
        page_data = page_data.order_by(form.order_by.data)
    page_data = page_data.paginate(error_out=False,page=int(form.page.data), per_page=10)
    r = {
        "has_next": page_data.has_next,
        "has_prev": page_data.has_prev,
        "pages": page_data.pages,
        "page": page_data.page,
        "total": page_data.total,
        "comments": [{
            "id": i.id,
            "user_name": BaseUser.query.filter(BaseUser.id == i.user_id).first().name,
            "name": Video.query.filter(Video.id == i.id).first().name,
            "user_id": i.user_id,
            "content": i.content,
            "create_time": i.create_time.strftime("%Y-%m-%d %H:%M:%S")
        } for i in page_data.items]
    }
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@comment.route('/load_comment')
def load_comment():
    """加载评论，用于观看视频时加载"""
    form = LoadComForm().validate_for_api()
    page_data = Comment.query.filter(Comment.video_id == form.video_id.data, Comment.root_id == None). \
        paginate(error_out=False,page=int(form.page.data), per_page=int(current_app.config["PER_COM_PAGE"]))
    comments = []
    for i in page_data.items:
        # 查找根节点评论下的评论
        reply = Comment.query.filter(Comment.root_id == i.id).all()
        reply_comments = []
        for j in reply:
            # 查找评论所属的用户
            baseuser = BaseUser.query.filter(BaseUser.id == j.user_id).first()
            user = User.query.filter(User.id == j.user_id).first()
            # 查找回复评论的用户
            reply_baseuser = None
            reply_user = None
            tmp_com = Comment.query.filter(Comment.id == j.parent_id).first()
            if tmp_com:
                # 如果评论的parent_id存在则说明有回复用户
                reply_baseuser = BaseUser.query.filter(BaseUser.id == tmp_com.user_id).first()
                reply_user = User.query.filter(User.id == tmp_com.user_id).first()
            reply_comment = {
                "id": j.id,
                "content": j.content,
                "create_time": j.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "user": {
                    "id": baseuser.id,
                    "name": baseuser.name,
                    "face": user.face,
                    "follownum": num_assign(Follow.query.filter(Follow.user_id == i.user_id).count()),
                    "fannum": num_assign(Follow.query.filter(Follow.follow_id == i.user_id).count()),
                    "info": user.info,
                    "gender": baseuser.gender
                },
                "reply_user": {
                    "id": reply_baseuser.id,
                    "name": reply_baseuser.name,
                    "face": reply_user.face,
                    "follownum": num_assign(Follow.query.filter(Follow.user_id == reply_baseuser.id).count()),
                    "fannum": num_assign(Follow.query.filter(Follow.follow_id == reply_baseuser.id).count()),
                    "info": reply_user.info,
                    "gender": reply_baseuser.gender
                } if reply_baseuser else None
            }
            reply_comments.append(reply_comment)
        # 查找当前根节点评论的所属用户
        user = User.query.filter(User.id == i.user_id).first()
        baseuser = BaseUser.query.filter(BaseUser.id == i.user_id).first()
        comment = {
            "id": i.id,
            "content": i.content,
            "create_time": i.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "user": {
                "id": baseuser.id,
                "name": baseuser.name,
                "face": user.face,
                "follownum": num_assign(Follow.query.filter(Follow.user_id == i.user_id).count()),
                "fannum": num_assign(Follow.query.filter(Follow.follow_id == i.user_id).count()),
                "info": user.info,
                "gender": baseuser.gender
            },
            "reply_comments": reply_comments
        }
        comments.append(comment)
    r = {
        "has_next": page_data.has_next,
        "has_prev": page_data.has_prev,
        "pages": page_data.pages,
        "page": page_data.page,
        "total": Comment.query.filter(Comment.video_id == form.video_id.data).count(),
        "comments": comments
    }
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@comment.route("/add_comment", methods=["POST"])
def add_comment():
    form = CommentAddForm().validate_for_api()
    with db.auto_commit():
        comment = Comment()
        if form.root_id.data:
            comment.root_id = int(form.root_id.data)
        if form.parent_id.data:
            comment.parent_id = int(form.parent_id.data)
        comment.video_id = form.video_id.data
        comment.content = form.content.data
        comment.user_id = current_user.id
        db.session.add(comment)
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")


@comment.route("/del_comment", methods=["GET"])
def del_comment():
    form = IdForm().validate_for_api()
    comment = Comment.query.filter(Comment.id == int(form.id.data), Comment.user_id == current_user.id). \
        first_or_404(description="找不到该评论")
    with db.auto_commit():
        # for i in Comment.query.filter(Comment.root_id == comment.id):
        #     db.session.delete(i)
        # 软删除
        comment.status = 0
        db.session.add(comment)
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")
