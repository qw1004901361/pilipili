# coding=UTF-8
import datetime

from app.forms.videoform import IndexForm
from app.libs.enums import FinishEnum, WeekEnum, ReturnEnum
from app.libs.redprint import Redprint
from app.models.video import Bangumi
from app.view_models.return_obj import ReturnObj

guochuang = Redprint("guochuang")


@guochuang.route("/get_timeline")
def get_timeline():
    """获取国创时间表"""
    select = Bangumi.query.filter(Bangumi.is_finish == FinishEnum.UNFINISH.value,
                                  Bangumi.tag_id == 3)
    r = {}
    for i in range(1, 8):
        bangumis = select.filter(Bangumi.update_weekday == i).all()
        one = {
            "guochuangs": [{
                "id": j.id,
                "name": j.name,
                "logo": j.logo,
                "new_piece": j.new_piece,
                "update_time": j.update_time.strftime("%H:%M:%S"),
                "update_weekday": j.update_weekday,
                "date": datetime.datetime.now().date().strftime("%Y-%m-%d")
            } for j in bangumis]}
        r[str(i)] = one
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@guochuang.route("/get_index")
def get_index():
    """获取番剧索引"""
    form = IndexForm().validate_for_api()
    select = Bangumi.query.filter(Bangumi.tag_id == 3)

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

    page_data = select.order_by(order).paginate(page=int(form.page.data), per_page=20)

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
            "playnum": i.playnum,
            "fannum": i.fannum,
            "score": i.score,
            "start_date": i.start_date.strftime("%Y-%m-%d")
        } for i in page_data.items]
    }
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)
