# coding=UTF-8
import datetime

from sqlalchemy import Text
from wtforms import StringField, IntegerField, DateTimeField, SelectField, FileField
from wtforms.validators import DataRequired, NumberRange, ValidationError

from app.forms.baseform import BaseForm
from app.models.video import UploadVideo, Verification


class NormalForm(BaseForm):
    tag_id = IntegerField("tag_id", default=-1)
    number = IntegerField("number", default=5)
    time = DateTimeField("time", default=datetime.datetime.now())


class NewForm(BaseForm):
    tag_id = IntegerField("tag_id", default=-1)
    number = IntegerField("number", default=10)


class RankForm(BaseForm):
    tag_id = IntegerField("tag_id", default=-1)
    number = IntegerField("number", default=5)
    time = IntegerField("time", default=100)


# def validate_time(self, field):
#     try:
#         NormalForm.time.data = datetime.datetime.strptime(field.data, "Y-%m-%d %H:%M:%S")
#     except Exception:
#         NormalForm.time.data = datetime.datetime.now()


class IndexForm(BaseForm):
    """番剧索引"""
    page = IntegerField("页码", default=1, validators=[NumberRange(min=1, message="页码不能小于一")])
    # 地区，默认为全部，0为日本，1为美国
    area = IntegerField("area", default=-1)
    # 是否完结，默认为全部，0为连载，1为完结
    is_finish = IntegerField("is_finish", default=-1)
    # 哪个月的番剧，默认为全部，1为一月，2为4月，3为7月，4为10月
    season = IntegerField("season", default=-1)
    # 年份，默认为全部
    pub_date = IntegerField("pub_date", default=-1)
    # 类型，1为追番人数，2为更新时间，3为最高评分，4为播放数量，5为开播时间，默认为1
    order = IntegerField("order", default=1)
    # 正序，倒序，默认为倒序
    sort = IntegerField("sort", default=0)


class UploadForm(BaseForm):
    """上传视频验证"""
    # 视频名
    name = StringField("标题", validators=[DataRequired("上传视频标题不能为空！")])
    # 视频资源路径
    url = FileField("视频")
    # 简介
    info = StringField(Text,validators=[DataRequired("视频简介不能为空！")])
    # 封面资源路径
    logo = FileField("视频封面")
    # 所属标签
    tag_id = IntegerField("所属类别", validators=[DataRequired("所属类别不能为空！")])


class VerificationForm(BaseForm):
    video_id = IntegerField("视频ID", validators=[DataRequired("视频ID不能为空！")])
    status = IntegerField("审核状态", validators=[DataRequired("审核状态为空！")])

    verification = None
    uploadvideo = None

    def validate_video_id(self, field):
        uploadvideo = UploadVideo.query.filter(UploadVideo.id == field.data).first()
        if not uploadvideo:
            raise ValidationError("该视频不存在")
        verification = Verification.query.filter(Verification.video_id == field.data).first()
        if not verification:
            raise ValidationError("审核项目不存在")
        self.verification = verification
        self.uploadvideo = uploadvideo
