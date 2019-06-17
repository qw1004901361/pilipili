# coding=UTF-8
import datetime
import random
import uuid

from flask import current_app
from flask_login import current_user
from sqlalchemy import or_

from app.forms.other import IdForm
from app.forms.videoform import NormalForm, RankForm, NewForm, TagForm
from app.libs.enums import ReturnEnum
from app.libs.redprint import Redprint
from app.libs.utils import num_assign, write_oplog
from app.models.base import db
from app.models.log import ViewLog
from app.models.user import BaseUser, User, Follow
from app.models.video import Video, Tag, Animation, VideoCol
from app.view_models.return_obj import ReturnObj

video = Redprint("video")


@video.route("/get_animation")
def get_animation():
    """获取轮播图"""
    form = NormalForm().validate_for_api()
    if form.tag_id.data == -1:
        animations = Animation.query.filter(Animation.tag_id == 0). \
            order_by(Animation.create_time.desc()).limit(form.number.data).all()
    else:
        animations = Animation.query.filter(Animation.tag_id == form.tag_id.data). \
            order_by(Animation.create_time.desc()).limit(form.number.data).all()
    r = {
        "animations": [{
            "name": i.name,
            "logo": i.logo,
            "url": i.url
        } for i in animations],
        "total": len(animations)
    }
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@video.route("/get_recommend")
def get_recommend():
    """获取首页及分区的推荐视频"""
    form = RankForm().validate_for_api()
    # 获取标签及其子标签
    sub_tags = [i.id for i in Tag.query.filter(Tag.parent_id == form.tag_id.data).all()]
    now_time = datetime.datetime.now()
    # now_time = now_time.replace(hour=12, minute=0, second=0)
    if form.tag_id.data == -1:
        videos = Video.query.filter(
            Video.release_time.between(now_time - datetime.timedelta(days=form.time.data), now_time)). \
            order_by(Video.score.desc()).limit(form.number.data).all()
    else:
        videos = Video.query.filter(
            Video.release_time.between(now_time - datetime.timedelta(days=form.time.data), now_time),
            or_(Video.tag_id == form.tag_id.data, Video.tag_id.in_(sub_tags))). \
            order_by(Video.score.desc()).limit(form.number.data).all()
    tmp = []
    for i in videos:
        baseuser = BaseUser.query.filter(BaseUser.id == i.user_id).first()
        video = {
            "id": i.id,
            "name": i.name,
            "playnum": num_assign(i.playnum),
            "logo": i.logo,
            "user": {
                "id": baseuser.id,
                "name": baseuser.name
            },
            "is_bangumi": False
        }
        tmp.append(video)
    r = {
        "time": form.time.data,
        "total": 8,
        "videos": tmp
    }
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@video.route("/get_rank")
def get_rank():
    """获取排行榜"""
    form = RankForm().validate_for_api()
    # 获取标签及其子标签
    sub_tags = [i.id for i in Tag.query.filter(Tag.parent_id == form.tag_id.data).all()]
    now_time = datetime.datetime.now()
    if form.tag_id.data == -1:
        videos = Video.query.filter(
            Video.release_time.between(now_time - datetime.timedelta(days=form.time.data), now_time)). \
            order_by(Video.score.desc()).limit(form.number.data).all()
    else:
        videos = Video.query.filter(
            Video.release_time.between(now_time - datetime.timedelta(days=form.time.data), now_time), or_(
                Video.tag_id == form.tag_id.data, Video.tag_id.in_(sub_tags))). \
            order_by(Video.score.desc()).limit(form.number.data).all()
    tmp = []
    for i in videos:
        baseuser = BaseUser.query.filter(BaseUser.id == i.user_id).first()
        video = {
            "id": i.id,
            "name": i.name,
            "score": i.score,
            "info": i.info,
            "playnum": num_assign(i.playnum),
            "commentnum": num_assign(i.commentnum),
            "colnum": num_assign(i.colnum),
            "logo": i.logo,
            "user": {
                "id": baseuser.id,
                "name": baseuser.name
            },
            "is_bangumi": False,
            "release_time": i.release_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        tmp.append(video)
    tag = Tag.query.filter(Tag.id == form.tag_id.data).first()
    r = {
        "time": form.time.data,
        "tag": tag.name if tag else "全部",
        "total": len(videos),
        "videos": tmp
    }
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@video.route("/get_one")
def get_one():
    """通过视频id获取视频信息"""
    form = IdForm().validate_for_api()
    video = Video.query.filter(Video.id == form.id.data).first_or_404(description="找不到该视频资源")
    baseuser = BaseUser.query.filter(BaseUser.id == video.user_id).first()
    user = User.query.filter(User.id == baseuser.id).first() if baseuser else None
    # 子标签
    sub = Tag.query.filter(Tag.id == video.tag_id).first()
    # 父标签
    index = Tag.query.filter(Tag.id == sub.parent_id).first() if sub else None
    r = {
        "id": video.id,
        "name": video.name,
        "url": video.url,
        "logo": video.logo,
        "info": video.info,
        "user": {
            "id": baseuser.id,
            "name": baseuser.name,
            "face": user.face,
            "fannum": num_assign(Follow.query.filter(Follow.follow_id == baseuser.id).count()),
            "follownum": num_assign(Follow.query.filter(Follow.user_id == baseuser.id).count()),
            "info": user.info
        } if baseuser else None,
        "tag": {
            "id": index.id if index else None,
            "name": index.name if index else None,
            "sub_id": sub.id if sub else None,
            "sub_name": sub.name if sub else None
        },
        "is_bangumi": False,
        "playnum": num_assign(video.playnum),
        "commentnum": num_assign(video.commentnum),
        "colnum": num_assign(video.colnum),
        "release_time": video.release_time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with db.auto_commit():
        viewlog = ViewLog.query.filter(ViewLog.user_id == current_user.id,
                                       ViewLog.video_id == video.id).first()
        if not viewlog:
            viewlog = ViewLog()
            viewlog.user_id = current_user.id
            viewlog.video_id = video.id
        viewlog.update_time = datetime.datetime.now()
        db.session.add(viewlog)
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@video.route("/get_newest")
def get_newest():
    """获取最新动态"""
    form = NewForm().validate_for_api()
    tag = None
    if form.tag_id.data == -1:
        videos = Video.query.limit(form.number.data).all()
    else:
        # 获取标签及其子标签
        sub_tags = [i.id for i in Tag.query.filter(Tag.parent_id == form.tag_id.data).all()]
        videos = Video.query.filter(or_(Video.tag_id == form.tag_id.data, Video.tag_id.in_(sub_tags))).order_by(
            Video.create_time.desc()).limit(form.number.data).all()
        tag = Tag.query.filter(Tag.id == form.tag_id.data).first()
    random.shuffle(videos)
    r = {
        "tag": tag.name if tag else "全部",
        "total": len(videos),
        "videos": [{
            "id": i.id,
            "name": i.name,
            "playnum": num_assign(i.playnum),
            "commentnum": num_assign(i.commentnum),
            "logo": i.logo,
            "length": i.length,
            "is_bangumi": False
        } for i in videos]
    }
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@video.route("/get_latest")
def get_latest():
    """获取最新投稿"""
    form = NewForm().validate_for_api()
    tag = None
    if form.tag_id.data == -1:
        videos = Video.query.limit(form.number.data).all()
    else:
        # 获取标签及其子标签
        sub_tags = [i.id for i in Tag.query.filter(Tag.parent_id == form.tag_id.data).all()]
        videos = Video.query.filter(or_(Video.tag_id == form.tag_id.data, Video.tag_id.in_(sub_tags))).order_by(
            Video.create_time.desc()).limit(form.number.data).all()
        tag = Tag.query.filter(Tag.id == form.tag_id.data).first()
    random.shuffle(videos)
    r = {
        "tag": tag.name if tag else "全部",
        "total": len(videos),
        "videos": [{
            "id": i.id,
            "name": i.name,
            "playnum": num_assign(i.playnum),
            "commentnum": num_assign(i.commentnum),
            "logo": i.logo,
            "length": i.length,
            "is_bangumi": False
        } for i in videos]
    }
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@video.route("/change_videocol")
def change_videocol():
    """视频收藏（点击为添加，再点击为取消）"""
    form = IdForm().validate_for_api()
    with db.auto_commit():
        videocol = VideoCol.query.filter(VideoCol.user_id == current_user.id,
                                         VideoCol.video_id == form.id.data).first()
        if videocol:
            videocol.status = 0 if videocol.status else 1
        else:
            videocol = VideoCol(user_id=current_user.id, video_id=form.id.data)
        db.session.add(videocol)
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")


@video.route("/get_relevant")
def get_relevant():
    """获得视频页面下的相关推荐视频"""
    form = TagForm().validate_for_api()
    videos = Video.query.filter(Video.tag_id == form.tag_id.data). \
        order_by(Video.create_time.desc()).limit(30).all()
    random.shuffle(videos)
    if len(videos) <= 10:
        pass
    else:
        videos = random.sample(videos, random.randint(len(videos) - random.randint(2, 9), len(videos)))
    tmp = []
    for i in videos:
        baseuser = BaseUser.query.filter(BaseUser.id == i.user_id).first()
        video = {
            "id": i.id,
            "name": i.name,
            "logo": i.logo,
            "playnum": num_assign(i.playnum),
            "commentnum": num_assign(i.commentnum),
            "user": {
                "id": baseuser.id,
                "name": baseuser.name
            },
            "length": i.length,
            "is_bangumi": False
        }
        tmp.append(video)
    r = {
        "total": len(videos),
        "videos": tmp
    }
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)
