# coding=UTF-8
import os
import shutil
import uuid
from datetime import datetime
from urllib.parse import urljoin

from flasgger import swag_from
from flask import current_app, request
from flask_login import login_required, current_user
from moviepy.video.io.VideoFileClip import VideoFileClip
from sqlalchemy import or_
from werkzeug.utils import secure_filename

from app.forms.other import PageForm, IdForm, VideoAddForm, SearchForm, VideoEditForm, ListVideoForm, \
    ListUploadVideoForm
from app.forms.videoform import VerificationForm
from app.libs.auth import user_auth
from app.libs.enums import ReturnEnum
from app.libs.redprint import Redprint
from app.libs.utils import make_dir, change_filename, allowed_image_file, allowed_video_file, write_oplog
from app.models.base import db
from app.models.user import BaseUser
from app.models.video import Video, Tag, UploadVideo, Verification
from app.view_models.return_obj import ReturnObj

"""
视频模块（视频管理员，超级管理员）
添加视频
列出视频
编辑视频
删除视频
查看审核视频
更改审核状态
"""

video = Redprint("video")


@video.route("/add", methods=["POST"])
@login_required
# @user_auth
@swag_from("../../yml/admin/video/add_video.yml")
def add_video():
    form = VideoAddForm()
    # 每次刷新列表，动态加载最新的标签
    # form.tag_id.choices = [(v.id, v.name) for v in Tag.query.all()]
    form.validate_for_api()
    with db.auto_commit():
        video = Video()
        video.name = form.name.data
        try:
            file = request.files[form.url.name]
            if not allowed_video_file(file.filename):
                return ReturnObj.get_response(ReturnEnum.VIDEO_TYPE_ERROR.value, "只允许上传mp4 avi flv wmv格式")
            file_url = secure_filename(file.filename)
            url = change_filename(file_url)
            file.save(os.path.join(current_app.config["VIDEO_DIR"], url))
            try:
                video_clip = VideoFileClip(os.path.join(current_app.config["VIDEO_DIR"], url))
                video.length = video_clip.duration
                video_clip.reader.close()
                video_clip.audio.reader.close_proc()
            except Exception as e:
                print(e)
                video.length = None
            video.url = urljoin(current_app.config["VIDEO_PATH"], url)
        except Exception as e:
            return ReturnObj.get_response(ReturnEnum.UPLOAD_VIDEO.value, "请上传视频")
        try:
            file = request.files[form.logo.name]
            if not allowed_image_file(file.filename):
                return ReturnObj.get_response(ReturnEnum.IMAGE_TYPE_ERROR.value, "只允许上传png jpg jpeg gif格式")
            file_logo = secure_filename(file.filename)
            logo = change_filename(file_logo)
            file.save(os.path.join(current_app.config["LOGO_DIR"], logo))
            video.logo = urljoin(current_app.config["LOGO_PATH"], logo)
        except Exception as e:
            return ReturnObj.get_response(ReturnEnum.UPLOAD_VIDEO_LOGO.value, "请上传视频封面")
        # 默认所属用户为pilipili番剧
        video.user_id = 6666
        video.info = form.info.data
        # 默认所属标签为连载动画
        video.tag_id = 18
        db.session.add(video)
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")


@video.route("/list")
@login_required
# @user_auth
@swag_from("../../yml/admin/video/list_video.yml")
def list_video():
    form = PageForm().validate_for_api()
    page_data = Video.query
    if form.tag_id.data == -1:
        pass
    else:
        sub_tags = [i.id for i in Tag.query.filter(Tag.parent_id == form.tag_id.data).all()]
        page_data = page_data.filter(or_(Video.tag_id == form.tag_id.data, Video.tag_id.in_(sub_tags)))
    if form.q.data:
        page_data = page_data.filter(or_(Video.id == form.q.data, Video.name.like("%" + form.q.data + "%")))
    page_data = page_data.order_by(Video.create_time.desc()). \
        paginate(error_out=False, page=int(form.page.data), per_page=int(form.pagesize.data))
    videos = []
    for i in page_data.items:
        tag = Tag.query.filter(Tag.id == i.tag_id).first()
        video = {
            "id": i.id,
            "name": i.name,
            "logo": i.logo,
            "playnum": i.playnum,
            "commentnum": i.commentnum,
            "danmunum": i.danmunum,
            "colnum": i.colnum,
            "url": i.url,
            "info": i.info,
            "tag": {
                "id": tag.id if tag else "未知",
                "name": tag.name if tag else "未知",
            },
            "release_time": i.release_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        videos.append(video)
    r = {
        "has_next": page_data.has_next,
        "has_prev": page_data.has_prev,
        "pages": page_data.pages,
        "page": page_data.page,
        "total": page_data.total,
        "videos": videos
    }
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@video.route("/edit", methods=["POST"])
@login_required
# @user_auth
@swag_from("../../yml/admin/video/edit_video.yml")
def edit_video():
    form = VideoEditForm()
    # form.tag_id.choices = [(v.id, v.name) for v in Tag.query.all()]
    form.validate_for_api()
    # 验证通过，从obj中获取查找到的对象
    video = form.obj
    with db.auto_commit():
        if form.name.data:
            video.name = form.name.data
        if form.info.data:
            video.info = form.info.data
        try:
            file = request.files[form.url.name]
            if not allowed_video_file(file.filename):
                return ReturnObj.get_response(ReturnEnum.VIDEO_TYPE_ERROR.value, "只允许上传mp4 avi flv wmv格式")
            file_url = secure_filename(file.filename)
            url = change_filename(file_url)
            file.save(os.path.join(current_app.config["VIDEO_DIR"], url))
            try:
                video_clip = VideoFileClip(os.path.join(current_app.config["VIDEO_DIR"], url))
                video.length = video_clip.duration
                video_clip.reader.close()
                video_clip.audio.reader.close_proc()
            except Exception as e:
                print(e)
                video.length = None
            video.url = urljoin(current_app.config["VIDEO_PATH"], url)
        except Exception as e:
            pass
        try:
            file = request.files[form.logo.name]
            if not allowed_image_file(file.filename):
                return ReturnObj.get_response(ReturnEnum.IMAGE_TYPE_ERROR.value, "只允许上传png jpg jpeg gif格式")
            file_logo = secure_filename(file.filename)
            logo = change_filename(file_logo)
            file.save(os.path.join(current_app.config["LOGO_DIR"], logo))
            video.logo = urljoin(current_app.config["LOGO_PATH"], logo)
        except Exception as e:
            pass
        # if form.tag_id.data:
        #     video.tag_id = form.tag_id.data
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")


@video.route("/del")
@login_required
# @user_auth
@swag_from("../../yml/admin/video/del_video.yml")
def del_video():
    form = IdForm().validate_for_api()
    video = Video.query.get_or_404(form.id.data, "找不到该视频")
    with db.auto_commit():
        db.session.delete(video)
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")


@video.route("/list_uploadvideo")
@login_required
@swag_from("../../yml/admin/video/list_uploadvideo.yml")
def list_uploadvideo():
    """查看审核视频"""
    form = ListUploadVideoForm().validate_for_api()
    page_data = UploadVideo.query
    if form.status.data == -1:
        pass
    else:
        page_data = page_data.join(Verification, UploadVideo.id == Verification.video_id). \
            filter(Verification.status == form.status.data)
    page_data = page_data.order_by(UploadVideo.create_time.asc()). \
        paginate(error_out=False, page=int(form.page.data), per_page=int(form.pagesize.data))
    uploadvideos = []
    for i in page_data.items:
        tag = Tag.query.filter(Tag.id == i.tag_id).first()
        baseuser = BaseUser.query.filter(BaseUser.id == i.user_id).first()
        one = {
            "id": i.id,
            "name": i.name,
            "url": i.url,
            "info": i.info,
            "logo": i.logo,
            "tag": {
                "id": tag.id if tag else "未知",
                "name": tag.name if tag else "未知"
            },
            "user": {
                "id": baseuser.id if baseuser else "未知",
                "name": baseuser.name if baseuser else "未知",
            },
            "upload_time": i.upload_time
        }
        uploadvideos.append(one)
    r = {
        "has_next": page_data.has_next,
        "has_prev": page_data.has_prev,
        "pages": page_data.pages,
        "page": page_data.page,
        "total": page_data.total,
        "uploadvideos": uploadvideos
    }
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@video.route("/edit_uploadvideo")
@login_required
@swag_from("../../yml/admin/video/edit_uploadvideo.yml")
def edit_uploadvideo():
    """编辑审核状态"""
    form = VerificationForm().validate_for_api()
    verification = form.verification
    uploadvideo = form.uploadvideo
    with db.auto_commit():
        verification.status = form.status.data
        verification.admin_id = current_user.id
        db.session.add(verification)
    if verification.status == 1:
        # 审核通过
        with db.auto_commit():
            # 审核通过，添加到视频表
            video = Video()
            video.user_id = uploadvideo.user_id
            video.tag_id = uploadvideo.tag_id
            video.name = uploadvideo.name
            video.info = uploadvideo.info

            # 更换视频封面文件位置
            file_name = uploadvideo.logo.rsplit("/", 1)[1]
            src = os.path.join(current_app.config["TMP_DIR"], file_name)
            if os.path.isfile(src):
                des = os.path.join(current_app.config["LOGO_DIR"], file_name)
                shutil.move(src, des)
            else:
                return ReturnObj.get_response(ReturnEnum.UPLOAD_VIDEO_LOGO.value, "上传视频封面不存在")
            video.logo = uploadvideo.logo.replace("tmp", "logo")

            # 更换视频文件位置
            file_name = uploadvideo.url.rsplit("/", 1)[1]
            src = os.path.join(current_app.config["TMP_DIR"], file_name)
            if os.path.isfile(src):
                des = os.path.join(current_app.config["VIDEO_DIR"], file_name)
                shutil.move(src, des)
            else:
                return ReturnObj.get_response(ReturnEnum.UPLOADVIDE0_NOT_EXIST.value, "上传视频不存在")
            video.url = uploadvideo.url.replace("tmp", "video")

            video.release_time = datetime.now()
            db.session.add(video)
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")
