# coding=UTF-8
import datetime
import random

from flask_login import current_user, login_required
from sqlalchemy import or_

from app.forms.other import IdForm
from app.forms.user import CancelColForm
from app.forms.videoform import IndexForm, RankForm
from app.libs.enums import FinishEnum, WeekEnum, ReturnEnum
from app.libs.redprint import Redprint
from app.libs.utils import num_assign
from app.models.base import db
from app.models.user import BaseUser
from app.models.video import Bangumi, Episode, Video, BangumiCol, Tag
from app.view_models.return_obj import ReturnObj

bangumi = Redprint("bangumi")


@bangumi.route("/get_one")
def get_one():
    """通过bangumi的id获取信息"""
    form = IdForm().validate_for_api()
    bangumi = Bangumi.query.filter(Bangumi.id == form.id.data, Bangumi.status == 1).\
        first_or_404(description="找不到该番剧")
    videos = [{"video_id": i.video_id, "piece": i.piece} for i in
              Episode.query.filter(Episode.bangumi_id == bangumi.id).all()]
    episodes = []
    for i in videos:
        video = Video.query.filter(Video.id == i["video_id"]).first()
        episode = {
            "id": video.id,
            "piece": i["piece"],
            "name": video.name,
            "logo": video.logo,
            "is_bangumi": True
        }
        episodes.append(episode)
    r = {
        "id": bangumi.id,
        "name": bangumi.name,
        "logo": bangumi.logo,
        "info": bangumi.info,
        "playnum": num_assign(bangumi.playnum),
        "commentnum": num_assign(bangumi.commentnum),
        "colnum": num_assign(bangumi.colnum),
        "fannum": num_assign(bangumi.fannum),
        "score": bangumi.score,
        "episodes": episodes,
        "is_finish": bangumi.is_finish,
        "start_date": bangumi.start_date.strftime("%Y-%m-%d"),
        "update_time": bangumi.update_time.strftime("%H:%M:%S"),
        "update_weekday": bangumi.update_weekday
    }
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@bangumi.route("/get_recommend")
def get_recommend():
    """获取番剧页面下的推荐番剧"""
    bangumis = Bangumi.query.filter(Bangumi.status == 1).order_by(Bangumi.score.desc()).limit(20).all()
    tmp = []
    for i in range(5):
        bangumi = bangumis[random.randint(0, 19)]
        one = {
            "id": bangumi.id,
            "name": bangumi.name,
            "logo": bangumi.logo
        }
        tmp.append(one)
    r = {
        "total": 5,
        "bangumis": tmp
    }
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@bangumi.route("/get_relevant")
def get_relevant():
    """获取番剧页面下的相关推荐视频"""
    videos = Video.query.filter(Video.name.like("%" + "" + "%")).limit(10).all()
    r = {
        "total": 10,
        "videos": [{
            "id": i.id,
            "name": i.name,
            "logo": i.logo,
            "playnum": num_assign(i.playnum),
            "commentnum": num_assign(i.commentnum),
            "length": i.length
        } for i in videos]}
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@bangumi.route("/get_timeline")
def get_timeline():
    """获取新番时间表"""
    select = Bangumi.query.filter(Bangumi.is_finish == FinishEnum.UNFINISH.value,
                                  Bangumi.tag_id == 2, Bangumi.status == 1)
    r = {}
    for i in range(1, 8):
        bangumis = select.filter(Bangumi.update_weekday == i).all()
        one = {
            "bangumis": [{
                "id": j.id,
                "name": j.name,
                "logo": j.logo,
                "new_piece": j.new_piece,
                "update_time": j.update_time.strftime("%H:%M:%S"),
                "update_weekday": j.update_weekday,
                "date": datetime.datetime.now().date().strftime("%Y-%m-%d")
            } for j in bangumis]}
        r[WeekEnum(i).name] = one
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@bangumi.route("/get_index")
# @login_required
def get_index():
    """获取番剧索引"""
    form = IndexForm().validate_for_api()
    select = Bangumi.query.filter(Bangumi.tag_id == 2, Bangumi.status == 1)

    # 地区筛选
    if form.area.data == -1:
        pass
    elif form.area.data == 0:
        select = select.filter(Bangumi.area == "日本")
    elif form.area.data == 1:
        select = select.filter(Bangumi.area == "美国")

    # 是否完结筛选
    if form.is_finish.data == -1:
        pass
    elif form.is_finish.data == 0:
        select = select.filter(Bangumi.is_finish == 0)
    elif form.is_finish.data == 1:
        select = select.filter(Bangumi.is_finish == 1)

    # 季节筛选
    if form.season.data == -1:
        pass
    elif form.season.data == 1:
        select = select.filter(Bangumi.season == 1)
    elif form.season.data == 2:
        select = select.filter(Bangumi.is_finish == 2)
    elif form.season.data == 3:
        select = select.filter(Bangumi.is_finish == 3)
    elif form.season.data == 4:
        select = select.filter(Bangumi.is_finish == 4)

    # 年份筛选
    if form.pub_date.data == -1:
        pass
    else:
        select = select.filter(Bangumi.start_date.between(
            datetime.date(year=form.pub_date.data, month=1, day=1), datetime.datetime.now().date()))

    # 类型筛选
    if form.order.data == 1:
        order = Bangumi.fannum
    elif form.order.data == 2:
        order = Bangumi.update_time
    elif form.order.data == 3:
        order = Bangumi.score
    elif form.order.data == 4:
        order = Bangumi.playnum
    elif form.order.data == 5:
        order = Bangumi.start_date

    if form.sort.data == 0:
        order = order.desc()

    page_data = select.order_by(order).paginate(error_out=False,page=int(form.page.data), per_page=20)

    r = {
        "has_next": page_data.has_next,
        "has_prev": page_data.has_prev,
        "pages": page_data.pages,
        "page": page_data.page,
        "total": page_data.total,
        "bangumis": [{
            "id": i.id,
            "name": i.name,
            "logo": i.logo,
            "playnum": num_assign(i.playnum),
            "fannum": num_assign(i.fannum),
            "score": i.score,
            "start_date": i.start_date.strftime("%Y-%m-%d")
        } for i in page_data.items]
    }
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@bangumi.route("/get_rank")
def get_rank():
    """获取番剧/国产动画排行榜"""
    form = RankForm().validate_for_api()
    if form.tag_id.data == -1 or form.tag_id.data == 2:
        # 查找番剧排行榜
        bangumis = Bangumi.query.filter(Bangumi.tag_id == 2, Bangumi.status == 1).order_by(
            Bangumi.score.desc()).limit(form.number.data).all()
    else:
        # 查找国产动画排行榜
        bangumis = Bangumi.query.filter(Bangumi.tag_id == 1, Bangumi.status == 1).order_by(
            Bangumi.score.desc()).limit(form.number.data).all()
    tmp = []
    for i in bangumis:
        fannum = BangumiCol.query.filter(BangumiCol.bangumi_id == i.id).count()
        bangumi = {
            "id": i.id,
            "name": i.name,
            "score": i.score,
            "playnum": num_assign(i.playnum),
            "commentnum": num_assign(i.commentnum),
            "colnum": num_assign(i.colnum),
            "fannum": num_assign(fannum),
            "logo": i.logo,
            "new_piece": i.new_piece,
            "is_finish": i.is_finish,
            "episodes": i.episodes
        }
        tmp.append(bangumi)
    r = {
        "time": form.time.data,
        "tag": "国产动画" if form.tag_id.data == 1 else "番剧",
        "total": len(bangumis),
        "bangumis": tmp
    }
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@bangumi.route("/change_bangumicol")
def change_bangumicol():
    """追番（点击为添加，再点击为取消）"""
    form = IdForm().validate_for_api()
    with db.auto_commit():
        bangumicol = BangumiCol.query.filter(BangumiCol.user_id == current_user.id,
                                             BangumiCol.bangumi_id == form.id.data).first()
        if bangumicol:
            bangumicol.status = 0 if bangumicol.status else 1
        else:
            bangumicol = BangumiCol(user_id=current_user.id, bangumi_id=form.id.data)
        db.session.add(bangumicol)
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")
