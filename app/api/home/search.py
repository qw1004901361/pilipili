# coding=UTF-8
import datetime
import random

from flask import request
from sqlalchemy import or_

from app.forms.other import IdForm, SearchForm, SearchVideoForm
from app.forms.videoform import IndexForm
from app.libs.enums import FinishEnum, WeekEnum, ReturnEnum
from app.libs.redprint import Redprint
from app.libs.utils import num_assign
from app.models.user import BaseUser, User, Follow
from app.models.video import Bangumi, Episode, Video, Tag
from app.view_models.return_obj import ReturnObj

search = Redprint("search")


@search.route("/search_video")
def search_video():
    """根据名字或者ID搜索视频"""
    form = SearchVideoForm().validate_for_api()
    select = Video.query.filter(Video.tag_id != None)
    # 排序筛选
    order = Video.score.desc()
    if form.order.data == -1:
        pass
    elif form.order.data == 1:
        order = Video.playnum.desc()
    elif form.order.data == 2:
        order = Video.release_time.desc()
    elif form.order.data == 3:
        order = Video.danmunum.desc()
    elif form.order.data == 4:
        order = Video.colnum.desc()

    # 时长筛选
    if form.length.data == -1:
        pass
    elif form.length.data == 1:
        select = select.filter(Video.length.between(0, 10 * 60))
    elif form.length.data == 2:
        select = select.filter(Video.length.between(10 * 60, 30 * 60))
    elif form.length.data == 3:
        select = select.filter(Video.length.between(30 * 60, 60 * 60))
    elif form.length.data == 4:
        select = select.filter(Video.length > 60 * 60)

    # 分区筛选
    if form.tag_id.data == -1:
        pass
    else:
        select = select.filter(Video.tag_id == form.tag_id.data)
    page_data = select.filter(
        or_(Video.name.like("%" + form.q.data + "%"), Video.id == form.q.data.lower().replace("av", ""))).order_by(
        order).paginate(error_out=False, page=int(form.page.data), per_page=20)
    videos = []
    for i in page_data.items:
        baseuser = BaseUser.query.filter(BaseUser.id == i.user_id).first()
        video = {
            "id": i.id,
            "name": i.name,
            "length": i.length,
            "playnum": num_assign(i.playnum),
            "logo": i.logo,
            "user": {
                "id": baseuser.id,
                "name": baseuser.name
            } if baseuser else None,
            "release_time": i.release_time.strftime("%Y-%m-%d"),
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
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@search.route("/search_bangumi")
def search_bangumi():
    """根据名字搜索番剧"""
    form = SearchForm().validate_for_api()
    page_data = Bangumi.query.filter(or_(Bangumi.id == form.q.data, Bangumi.name.like("%" + form.q.data + "%"))). \
        paginate(error_out=False, page=int(form.page.data), per_page=20)
    bangumis = []
    for i in page_data.items:
        episodes = []
        for j in Episode.query.filter(Episode.bangumi_id == i.id).all():
            video = Video.query.filter(Video.id == j.video_id).first()
            episode = {
                "piece": j.piece,
                "video": {
                    "id": video.id,
                    "url": video.url,
                } if video else None
            }
            episodes.append(episode)
        bangumi = {
            "id": i.id,
            "name": i.name,
            "info": i.info,
            "logo": i.logo,
            "start_date": i.start_date.strftime("%Y-%m-%d"),
            "area": i.area,
            "grade": i.grade,
            "episodes": episodes,
            "voice_actors": i.voice_actors,
            "tag": "国产" if i.tag_id == 1 else ("日漫" if i.tag_id == 2 else "其他")
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
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@search.route("/search_user")
def search_user():
    """搜索用户"""
    form = SearchForm().validate_for_api()
    page_data = BaseUser.query.filter(BaseUser.name.like("%" + form.q.data + "%")). \
        paginate(error_out=False, page=int(form.page.data), per_page=20)
    baseusers = []
    for i in page_data.items:
        user = User.query.filter(User.id == i.id).first()
        baseuser = {
            "id": i.id,
            "name": i.name,
            "info": user.info,
            "face": user.face,
            "post_num": 0,
            "fannum": num_assign(Follow.query.filter(Follow.follow_id == i.id).count()),
            "follownum": num_assign(Follow.query.filter(Follow.user_id == i.id).count()),
        }
        baseusers.append(baseuser)
    r = {
        "has_next": page_data.has_next,
        "has_prev": page_data.has_prev,
        "pages": page_data.pages,
        "page": page_data.page,
        "total": page_data.total,
        "baseusers": baseusers
    }
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)
