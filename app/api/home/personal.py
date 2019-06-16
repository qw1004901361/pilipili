# coding=UTF-8
import datetime
import os
from urllib.parse import urljoin

import requests
from flask import current_app, request
from flask_login import login_required, current_user, logout_user
from lxml import etree
from werkzeug.utils import secure_filename

from app.forms.auth import PwdForm
from app.forms.other import PageForm, IdForm
from app.forms.user import UserEditForm, FanOrFollowForm, CancelColForm
from app.forms.videoform import UploadForm
from app.libs.auth import unload_auth
from app.libs.enums import GenderEnum, ReturnEnum
from app.libs.redprint import Redprint
from app.libs.utils import change_filename, num_assign, allowed_image_file, allowed_video_file
from app.models.base import db
from app.models.log import ViewLog, LoginLog
from app.models.user import BaseUser, User, Follow
from app.models.video import BangumiCol, Tag, VideoCol, Bangumi, Video, Comment, UploadVideo, Verification
from app.view_models.return_obj import ReturnObj

personal = Redprint("personal")


@personal.route("/get_user")
@login_required
def get_user():
    """查看用户信息"""
    baseuser = BaseUser.query.filter(BaseUser.id == current_user.id). \
        first_or_404(description="找不到该用户")
    user = User.query.filter(User.id == baseuser.id).first()
    r = {
        "user": {
            "id": baseuser.id,
            "name": baseuser.name,
            "account": baseuser.account,
            "gender": GenderEnum(baseuser.gender).name,
            "email": user.email if user else None,
            "phone": user.phone if user else None,
            "info": user.info if user else None,
            "face": user.face if user else None,
            "create_time": baseuser.create_time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "follownum": num_assign(Follow.query.filter(Follow.user_id == current_user.id).count()),
        "fannum": num_assign(Follow.query.filter(Follow.follow_id == current_user.id).count())
    }
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@personal.route("/get_fan_or_follow")
@login_required
def get_fan_or_follow():
    """查看粉丝或者关注"""
    form = FanOrFollowForm().validate_for_api()
    if form.tag_id.data == 1:
        # 查找粉丝，查找Follow表中follow_id等于自己的id
        fans = Follow.query.order_by(Follow.create_time.desc()).filter(Follow.follow_id == current_user.id).all()
        fans = [i.user_id for i in fans]
        r = {
            "fans": [{
                "id": i.id,
                "name": BaseUser.query.filter(BaseUser.id == i.id).first().name,
                "info": i.info,
                "follownum": num_assign(Follow.query.filter(Follow.user_id == current_user.id).count()),
                "fannum": num_assign(Follow.query.filter(Follow.follow_id == current_user.id).count()),
                "face": i.face
            } for i in User.query.filter(User.id.in_(fans))],
            "total": int(len(fans))
        }
    else:
        # 查找Follow表中user_id等于自己的id
        follows = Follow.query.filter(Follow.user_id == current_user.id).all()
        follows = [i.follow_id for i in follows]
        r = {
            "follows": [{
                "id": i.id,
                "name": BaseUser.query.filter(BaseUser.id == i.id).first().name,
                "info": i.info,
                "follownum": num_assign(Follow.query.filter(Follow.user_id == i.id).count()),
                "fannum": num_assign(Follow.query.filter(Follow.follow_id == i.id).count()),
                "face": i.face
            } for i in User.query.filter(User.id.in_(follows))],
            "total": int(len(follows))
        }
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@personal.route("/get_my_video")
@login_required
def get_my_video():
    """获取自己上传的视频"""
    form = PageForm().validate_for_api()
    page_data = Video.query.filter(Video.user_id == current_user.id).order_by(
        Video.create_time.desc()).paginate(error_out=False, page=int(form.page.data), per_page=20)
    videos = []
    for i in page_data.items:
        baseuser = BaseUser.query.filter(BaseUser.id == i.user_id).first()
        tmp = {
            "id": i.id,
            "name": i.name,
            "playnum": i.playnum,
            "colnum": i.colnum,
            "logo": i.logo,
            "user": {
                "id": baseuser.id,
                "name": baseuser.name,
            },
            "release_time": i.release_time.strftime("%Y-%m-%d %H:%M:%S"),
            "length": i.length,
        }
        videos.append(tmp)
    r = {
        "has_next": page_data.has_next,
        "has_prev": page_data.has_prev,
        "pages": page_data.pages,
        "page": page_data.page,
        "videos": videos,
        "total": page_data.total
    }
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@personal.route("/get_bangumicol")
@login_required
def get_bangumicol():
    """获取番剧订阅"""
    form = PageForm().validate_for_api()
    page_data = BangumiCol.query.filter(BangumiCol.user_id == current_user.id).order_by(
        BangumiCol.create_time.desc()).paginate(error_out=False, page=int(form.page.data), per_page=15)
    bangumis = []
    for i in page_data.items:
        bangumi = Bangumi.query.filter(Bangumi.id == i.bangumi_id).first()
        tag = Tag.query.filter(Tag.id == bangumi.tag_id).first()
        tmp = {
            "id": bangumi.id,
            "name": bangumi.name,
            "info": bangumi.info,
            "logo": bangumi.logo,
            "area": bangumi.area,
            "tag": tag.name if tag else "未知"
        }
        bangumis.append(tmp)
    r = {
        "has_next": page_data.has_next,
        "has_prev": page_data.has_prev,
        "pages": page_data.pages,
        "page": page_data.page,
        "bangumis": bangumis,
        "total": page_data.total
    }
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@personal.route("/get_videocol")
@login_required
def get_videocol():
    """获取视频收藏"""
    form = PageForm().validate_for_api()
    page_data = VideoCol.query.filter(VideoCol.user_id == current_user.id).order_by(
        VideoCol.create_time.desc()).paginate(error_out=False, page=int(form.page.data), per_page=20)
    videos = []
    for i in page_data.items:
        video = Video.query.filter(Video.id == i.video_id).first()
        baseuser = BaseUser.query.filter(BaseUser.id == video.user_id).first()
        tmp = {
            "id": video.id,
            "name": video.name,
            "playnum": video.playnum,
            "colnum": video.colnum,
            "logo": video.logo,
            "user": {
                "id": baseuser.id,
                "name": baseuser.name,
            },
            "release_time": video.release_time.strftime("%Y-%m-%d %H:%M:%S"),
            "length": video.length,
            "create_time": video.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        videos.append(tmp)
    r = {
        "has_next": page_data.has_next,
        "has_prev": page_data.has_prev,
        "pages": page_data.pages,
        "page": page_data.page,
        "videos": videos,
        "total": page_data.total
    }
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@personal.route("/cancel_videocol")
@login_required
def cancel_videocol():
    """取消（批量）视频收藏"""
    form = CancelColForm()
    form.video_id.choices = [(v.video_id, v.video_id) for v in
                             VideoCol.query.filter(VideoCol.user_id == current_user.id).all()]
    form.validate_for_api()
    for i in form.id.data:
        with db.auto_commit():
            col = VideoCol(user_id=current_user.id, video_id=i)
            if col:
                db.session.delete(col)
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")


@personal.route("/cancel_bangumicol")
@login_required
def cancel_bangumicol():
    """取消（批量）番剧收藏"""
    form = CancelColForm()
    form.video_id.choices = [(v.bangumi_id, v.bangumi_id) for v in
                             BangumiCol.query.filter(BangumiCol.user_id == current_user.id).all()]
    form.validate_for_api()
    for i in form.id.data:
        with db.auto_commit():
            col = BangumiCol(user_id=current_user.id, bangumi_id=i)
            if col:
                db.session.delete(col)
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")


@personal.route("/edit_user", methods=["POST"])
@login_required
def edit_user():
    """编辑用户信息"""
    form = UserEditForm().validate_for_api()
    baseuser = form.obj
    user = User.query.filter(User.id == baseuser.id).first()
    with db.auto_commit():
        if form.name.data:
            baseuser.name = form.name.data
        if form.email.data:
            user.email = form.email.data
        if form.phone.data:
            user.phone = form.phone.data
        if form.info.data:
            user.info = form.info.data
        try:
            a = request.files
            file = request.files[form.face.name]
            if not allowed_image_file(file.filename):
                return ReturnObj.get_response(ReturnEnum.IMAGE_TYPE_ERROR.value, "只允许上传png jpg jpeg gif格式")
            file_face = secure_filename(file.filename)
            face = change_filename(file_face)
            file.save(os.path.join(current_app.config["FACE_DIR"], face))
            user.face = urljoin(current_app.config["FACE_PATH"], face)
        except:
            pass
        db.session.add(baseuser)
        db.session.add(user)
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")


@personal.route("/pwd", methods=["POST"])
@login_required
def pwd():
    """修改密码"""
    form = PwdForm().validate_for_api()
    baseuser = BaseUser.query.filter(BaseUser.id == current_user.id).first_or_404(description="用户不存在")
    baseuser.pwd = form.new_pwd.data
    with db.auto_commit():
        db.session.add(baseuser)
    logout_user()
    # 清空加载的权限
    unload_auth()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "密码修改成功，请重新登陆")


@personal.route("/get_view_history")
@login_required
def get_view_history():
    """获取观看历史记录"""
    form = PageForm().validate_for_api()
    page_data = ViewLog.query.filter(ViewLog.user_id == current_user.id).order_by(
        ViewLog.update_time.asc()).paginate(error_out=False, page=int(form.page.data), per_page=20)
    videos = []
    for i in page_data.items:
        video = Video.query.filter(Video.id == i.video_id).frist()
        baseuser = BaseUser.query.filter(BaseUser.id == video.user_id).first()
        tag = Tag.query.filter(Tag.id == video.tag_id).first()
        tmp = {
            "id": video.id,
            "name": video.name,
            "logo": video.logo,
            "user": {
                "id": baseuser.id,
                "name": baseuser.name,
            } if baseuser else None,
            "tag": tag.name if tag else None,
            "time": i.update_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        videos.append(tmp)
    r = {
        "has_next": page_data.has_next,
        "has_prev": page_data.has_prev,
        "pages": page_data.pages,
        "page": page_data.page,
        "total": page_data.total,
        "videos": videos
    }
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@personal.route("/get_com_history")
@login_required
def get_com_history():
    """获取评论记录"""
    form = PageForm().validate_for_api()
    page_data = Comment.query.filter(Comment.user_id == current_user.id). \
        paginate(error_out=False, page=int(form.page.data), per_page=int(current_app.config["PER_PAGE_COM"]))
    comments = []
    for i in page_data.items:
        video = Video.query.filter(Video.id == i.video_id).frist()
        baseuser = BaseUser.query.filter(BaseUser.id == video.user_id).first()
        tag = Tag.query.filter(Tag.id == video.tag_id).first()
        tmp = {
            "id": video.id,
            "name": video.name,
            "logo": video.logo,
            "user": {
                "id": baseuser.id,
                "name": baseuser.name,
            } if baseuser else None,
            "tag": tag.name if tag else None,
            "time": i.update_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        comments.append(tmp)
    r = {
        "has_next": page_data.has_next,
        "has_prev": page_data.has_prev,
        "pages": page_data.pages,
        "page": page_data.page,
        "total": page_data.total,
        "comments": comments
    }
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@personal.route("/get_login_history")
@login_required
def get_login_history():
    """获取登录日志"""
    logs = LoginLog.query.order_by(LoginLog.create_time.desc()).limit(20).all()
    arrs = []
    for i in logs:
        tmp = i.ip.split(".")
        # ip = tmp[0] + "." + tmp[1] + "." + "***" + "." + "**"
        ip = ".".join([tmp[0], tmp[1], "***", "**"])
        arr = {
            "id": i.id,
            "ip": ip,
            "create_time": i.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "location": i.location
        }
        arrs.append(arr)
    r = {
        "logs": arrs,
        "total": 20
    }
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@personal.route("/change_follow")
@login_required
def change_follow():
    """关注（点击为关注，再点击为取关）"""
    form = IdForm().validate_for_api()
    with db.auto_commit():
        follow = Follow.query.filter(Follow.user_id == current_user.id,
                                     Follow.follow_id == form.id.data).first()
        if follow:
            follow.status = 0 if follow.status else 1
        else:
            follow = Follow(user_id=current_user.id, follow_id=form.id.data)
        db.session.add(follow)
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")


@personal.route("/upload_video", methods=["POST"])
@login_required
def upload_video():
    """上传视频，由管理员审核"""
    form = UploadForm().validate_for_api()
    try:
        # 添加到上传视频表
        uploadvideo = UploadVideo()
        uploadvideo.name = form.name.data
        uploadvideo.info = form.info.data
        uploadvideo.user_id = current_user.id
        uploadvideo.tag_id = form.tag_id.data
        # 保存视频封面
        try:
            file = request.files[form.logo.name]
            if not allowed_image_file(file.filename):
                return ReturnObj.get_response(ReturnEnum.IMAGE_TYPE_ERROR.value, "只允许上传png jpg jpeg gif格式")
            file_logo = secure_filename(file.filename)
            logo = change_filename(file_logo)
            file.save(os.path.join(current_app.config["TMP_DIR"], logo))
            uploadvideo.logo = urljoin(current_app.config["TMP_PATH"], logo)
        except Exception as e:
            return ReturnObj.get_response(ReturnEnum.UPLOAD_VIDEO_LOGO.value, "请上传视频封面")
        # 保存视频
        try:
            file = request.files[form.url.name]
            if not allowed_video_file(file.filename):
                return ReturnObj.get_response(ReturnEnum.VIDEO_TYPE_ERROR.value, "只允许上传mp4 avi flv wmv格式")
            file_url = secure_filename(file.filename)
            url = change_filename(file_url)
            file.save(os.path.join(current_app.config["TMP_DIR"], url))
            uploadvideo.url = urljoin(current_app.config["TMP_PATH"], url)
        except Exception as e:
            return ReturnObj.get_response(ReturnEnum.UPLOAD_VIDEO.value, "请上传视频")
        db.session.add(uploadvideo)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        return ReturnObj.get_response(ReturnEnum.ADD_UPLOADVIDE0_ERROR.value, "上传视频失败")
    try:
        # 添加审核状态
        uploadvideo = UploadVideo.query.filter(UploadVideo.name == uploadvideo.name,
                                               uploadvideo.user_id == current_user.id).first()
        verification = Verification()
        verification.video_id = uploadvideo.id
        db.session.add(verification)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        return ReturnObj.get_response(ReturnEnum.ADD_VERIFICATION_ERROR.value, "添加审核状态失败")
    r = {
        "url": uploadvideo.url,
        "logo": uploadvideo.logo
    }
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@personal.route("/get_all_tag")
@login_required
def get_all_tag():
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


def add_login_history():
    """添加登录记录"""
    log = LoginLog()
    with db.auto_commit():
        log.ip = request.remote_addr
        log.user_id = current_user.id
        db.session.add(log)
    # return ReturnObj.get_response(1004, "ok")


def add_view_history(video_id):
    """添加观看历史记录"""
    log = ViewLog.query.filter(ViewLog.user_id == current_user.id, ViewLog.video_id == video_id).first()
    if not log:
        log = ViewLog()
    with db.auto_commit():
        log.video_id = video_id
        log.user_id = current_user.id
        db.session.add(log)
    # return ReturnObj.get_response(1004, "ok")
