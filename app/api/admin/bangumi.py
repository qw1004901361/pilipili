# coding=UTF-8
import os
from urllib.parse import urljoin

from flasgger import swag_from
from flask import current_app, request
from flask_login import login_required
from moviepy.video.io.VideoFileClip import VideoFileClip
from sqlalchemy import or_
from werkzeug.utils import secure_filename

from app.forms.other import PageForm, IdForm, VideoAddForm, SearchForm, VideoEditForm, ListVideoForm, BangumiAddForm, \
    BangumiListForm, BangumiEditForm, BangumiAddVideoForm
from app.libs.auth import user_auth
from app.libs.enums import ReturnEnum
from app.libs.redprint import Redprint
from app.libs.utils import make_dir, change_filename, allowed_image_file, allowed_video_file, write_oplog
from app.models.base import db
from app.models.video import Video, Tag, Bangumi, Episode
from app.view_models.return_obj import ReturnObj

"""
番剧模块（视频管理员，超级管理员）
添加番剧
列出番剧
编辑番剧
删除番剧
查询番剧
添加番剧视频
"""

bangumi = Redprint("bangumi")


@bangumi.route("/add", methods=["POST"])
@login_required
# @user_auth
@swag_from("../../yml/admin/bangumi/add_bangumi.yml")
def add_bangumi():
    form = BangumiAddForm().validate_for_api()
    with db.auto_commit():
        bangumi = Bangumi()
        bangumi.name = form.name.data
        bangumi.info = form.info.data
        if form.voice_actors.data:
            bangumi.voice_actors = form.voice_actors.data
        if form.staff.data:
            bangumi.staff = form.staff.data
        try:
            file = request.files[form.logo.name]
            if not allowed_image_file(file.filename):
                return ReturnObj.get_response(ReturnEnum.IMAGE_TYPE_ERROR.value, "只允许上传png jpg jpeg gif格式")
            file_logo = secure_filename(file.filename)
            logo = change_filename(file_logo)
            file.save(os.path.join(current_app.config["LOGO_DIR"], logo))
            bangumi.logo = urljoin("http://localhost:5000/static/logo/", logo)
        except Exception as e:
            pass
        if form.start_date.data:
            bangumi.start_date = form.start_date.data
        if form.update_time.data:
            bangumi.update_time = form.update_time.data
        if form.update_weekday.data:
            bangumi.update_weekday = form.update_weekday.data
        if form.season.data:
            bangumi.season = form.season.data
        if form.area.data:
            bangumi.area = form.area.data
        if form.tag_id.data:
            bangumi.tag_id = form.tag_id.data
        db.session.add(bangumi)
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")


@bangumi.route("/list")
@login_required
# @user_auth
@swag_from("../../yml/admin/bangumi/list_bangumi.yml")
def list_bangumi():
    form = PageForm().validate_for_api()
    page_data = Bangumi.query
    if form.tag_id.data == -1:
        pass
    else:
        page_data = page_data.filter(Bangumi.tag_id == form.tag_id.data)
    if form.q.data:
        page_data = page_data.filter(or_(Bangumi.id == form.q.data, Bangumi.name.like("%" + form.q.data + "%")))
    page_data = page_data.order_by(Bangumi.create_time.desc()). \
        paginate(error_out=False, page=int(form.page.data), per_page=int(form.pagesize.data))
    bangumis = []
    for i in page_data.items:
        tag = "国产" if i.tag_id == 1 else ("日漫" if i.tag_id == 2 else "其他")
        bangumi = {
            "id": i.id,
            "name": i.name,
            "logo": i.logo,
            "playnum": i.playnum,
            "commentnum": i.commentnum,
            "danmunum": i.danmunum,
            "colnum": i.colnum,
            "fannum": i.fannum,
            "status": i.status,
            "tag": tag
        }
        bangumis.append(bangumi)
    r = {
        "has_next": page_data.has_next,
        "has_prev": page_data.has_prev,
        "pages": page_data.pages,
        "page": page_data.page,
        "total": page_data.total,
        "bangumis": bangumis
    }
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@bangumi.route("/edit", methods=["POST"])
@login_required
# @user_auth
@swag_from("../../yml/admin/bangumi/edit_bangumi.yml")
def edit_bangumi():
    form = BangumiEditForm().validate_for_api()
    bangumi = form.obj
    with db.auto_commit():
        if form.name.data:
            bangumi.name = form.name.data
        if form.info.data:
            bangumi.info = form.info.data
        if form.voice_actors.data:
            bangumi.voice_actors = form.voice_actors.data
        if form.staff.data:
            bangumi.staff = form.staff.data
        try:
            file = request.files[form.logo.name]
            if not allowed_image_file(file.filename):
                return ReturnObj.get_response(ReturnEnum.IMAGE_TYPE_ERROR.value, "只允许上传png jpg jpeg gif格式")
            file_logo = secure_filename(file.filename)
            logo = change_filename(file_logo)
            file.save(os.path.join(current_app.config["LOGO_DIR"], logo))
            bangumi.logo = urljoin("http://localhost:5000/static/logo/", logo)
        except Exception as e:
            pass
        if form.start_date.data:
            bangumi.start_date = form.start_date.data
        if form.update_time.data:
            bangumi.update_time = form.update_time.data
        if form.update_weekday.data:
            bangumi.update_weekday = form.update_weekday.data
        if form.season.data:
            bangumi.season = form.season.data
        if form.area.data:
            bangumi.area = form.area.data
        if form.tag_id.data:
            bangumi.tag_id = form.tag_id.data
        db.session.add(bangumi)
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")


@bangumi.route("/del")
@login_required
# @user_auth
@swag_from("../../yml/admin/bangumi/del_bangumi.yml")
def del_bangumi():
    form = IdForm().validate_for_api()
    bangumi = Bangumi.query.get_or_404(form.id.data, "找不到该番剧")
    with db.auto_commit():
        # 将状态设为0，下架
        bangumi.status = 0
        db.session.add(bangumi)
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")


# @bangumi.route("/view")
# @login_required
# # @user_auth
# @swag_from("../../yml/admin/bangumi/view_bangumi.yml")
# def view_bangumi():
#     """通过番剧ID或者番剧名搜索"""
#     form = SearchForm().validate_for_api()
#     q = form.q.data
#     select = Bangumi.query.filter(or_(Bangumi.id == q, Bangumi.name.like("%" + q + "%")))
#     page_data = select.paginate(error_out=False,page=int(form.page.data), per_page=int(current_app.config["ADMIN_PER_VIDEO_PAGE"]))
#     bangumis = []
#     for i in page_data.items:
#         tag = "国产" if i.tag_id == 1 else ("日漫" if i.tag_id == 2 else "其他")
#         bangumi = {
#             "id": i.id,
#             "name": i.name,
#             "logo": i.logo,
#             "playnum": i.playnum,
#             "commentnum": i.commentnum,
#             "danmunum": i.danmunum,
#             "colnum": i.colnum,
#             "fannum": i.fannum,
#             "release_time": i.release_time,
#             "status": i.status,
#             "tag": tag
#         }
#         bangumis.append(bangumi)
#     r = {
#         "has_next": page_data.has_next,
#         "has_prev": page_data.has_prev,
#         "pages": page_data.pages,
#         "page": page_data.page,
#         "total": page_data.total,
#         "bangumis": bangumis
#     }
#     write_oplog()
#     return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@bangumi.route("/add_video")
@login_required
# @user_auth
@swag_from("../../yml/admin/bangumi/add_video.yml")
def add_video():
    """添加番剧视频"""
    form = BangumiAddVideoForm().validate_for_api()
    bangumi = form.obj
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
            video.url = urljoin("http://localhost:5000/static/video/", url)
        except Exception as e:
            return ReturnObj.get_response(ReturnEnum.UPLOAD_VIDEO.value, "请上传视频")
        try:
            file = request.files[form.logo.name]
            if not allowed_image_file(file.filename):
                return ReturnObj.get_response(ReturnEnum.IMAGE_TYPE_ERROR.value, "只允许上传png jpg jpeg gif格式")
            file_logo = secure_filename(file.filename)
            logo = change_filename(file_logo)
            file.save(os.path.join(current_app.config["LOGO_DIR"], logo))
            video.logo = urljoin("http://localhost:5000/static/logo/", logo)
        except Exception as e:
            return ReturnObj.get_response(ReturnEnum.UPLOAD_VIDEO_LOGO.value, "请上传视频封面")
    video = Video.query.filter(Video.name == form.name.data).order_by(Video.create_time.desc()).first()
    with db.auto_commit():
        bangumi.episodes += 1
        bangumi.new_piece += 1
        if form.is_finish.data == 1:
            bangumi.is_finish = 1
    with db.auto_commit():
        episode = Episode()
        episode.video_id = video.id
        episode.bangumi_id = bangumi.id
        episode.piece = bangumi.new_piece
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")
