# coding=UTF-8
import datetime

from wtforms import StringField, IntegerField, FileField, TextAreaField, SelectField, DateField, DateTimeField, \
    TimeField
from wtforms.validators import DataRequired, ValidationError, Length, NumberRange, Regexp

from app.forms.baseform import BaseForm
from app.models.video import Tag, Video, Animation, Comment, Bangumi


class IdForm(BaseForm):
    """所有使用ID的查询"""
    id = StringField("id", validators=[DataRequired("id不能为空")])


class PageForm(BaseForm):
    """所有使用分页的查询"""
    page = IntegerField("页码", default=1, validators=[NumberRange(min=1, message="页码不能小于一")])
    pagesize = IntegerField("数量", default=10, validators=[NumberRange(min=1, message="数量不能小于一")])
    q = StringField("搜索关键字")
    tag_id = IntegerField("标签或者分类或者分区", default=-1)


class ListComForm(BaseForm):
    page = IntegerField("页码", default=1, validators=[NumberRange(min=1, message="页码不能小于一")])
    pagesize = IntegerField("数量", default=10, validators=[NumberRange(min=1, message="数量不能小于一")])
    q = StringField("搜索关键字")
    video_id = IntegerField("视频ID")


class ListLogForm(BaseForm):
    page = IntegerField("页码", default=1, validators=[NumberRange(min=1, message="页码不能小于一")])
    pagesize = IntegerField("数量", default=10, validators=[NumberRange(min=1, message="数量不能小于一")])
    q = StringField("搜索关键字")
    start_date = DateField("查询开始日期")
    end_date = DateField("查询结束日期", default=datetime.datetime.now)
    tag_id = IntegerField("标签或者分类或者分区", default=-1)
    video_id = IntegerField("视频ID")


class LoadComForm(BaseForm):
    video_id = StringField("视频id", validators=[DataRequired("视频id不能为空")])
    page = IntegerField("页码", default=1, validators=[NumberRange(min=1, message="页码不能小于一")])


class CommentAddForm(BaseForm):
    video_id = IntegerField("video_id", validators=[DataRequired("视频id不能为空")])
    root_id = StringField("回复的根评论id", default=None)
    parent_id = StringField("回复的评论id", default=None)
    content = StringField("内容", validators=[DataRequired("评论内容不能为空")])


# class ListComForm(BaseForm):
#     start_time = DateField("搜索开始时间")
#     end_time = DateField("搜索结束时间")
#     order_by = StringField("排序方式", default=Comment.create_time.asc())
#     page = IntegerField("页码", default=1, validators=[NumberRange(min=1, message="页码不能小于一")])


# class ListLogForm(BaseForm):
#     start_time = DateField("搜索开始时间")
#     end_time = DateField("搜索结束时间")
#     order_by = StringField("排序方式", default=UserLoginLog.create_time.asc())
#     page = IntegerField("页码", default=1, validators=[NumberRange(min=1, message="页码不能小于一")])


class SearchForm(BaseForm):
    q = StringField("搜索关键词", validators=[DataRequired("搜索关键词不能为空")])
    page = IntegerField("页码", default=1, validators=[NumberRange(min=1, message="页码不能小于一")])


class SearchVideoForm(BaseForm):
    q = StringField("搜索关键词", validators=[DataRequired("搜索关键词不能为空")])
    page = IntegerField("页码", default=1, validators=[NumberRange(min=1, message="页码不能小于一")])
    # 默认为综合排序，1为最多点击，2为最新发布，3为最多弹幕，4为最多收藏
    order = IntegerField("order", default=-1)
    # 默认为全部时长，1为1分钟以下，2为10-30分钟，3为30-60分钟，4为60分钟以上
    length = IntegerField("length", default=-1)
    # 默认为全部分区
    tag_id = IntegerField("tag", default=-1)


class TagAddForm(BaseForm):
    """添加标签"""
    name = StringField("标签名", validators=[DataRequired("标签名不能为空")])
    info = StringField("标签信息", validators=[DataRequired("标签信息不能为空")])
    parent_id = StringField("父标签")

    def validate_name(self, field):
        if Tag.query.filter(Tag.name == field.data).first():
            raise ValidationError("该标签已存在! ")

    def validate_parent_id(self, field):
        if not Tag.query.filter(Tag.id == field.data).first():
            raise ValidationError("父标签不存在! ")


class TagEditForm(BaseForm):
    """编辑标签"""
    id = StringField("id", validators=[DataRequired("id不能为空")])
    name = StringField("标签名")
    info = StringField("标签信息")
    parent_id = StringField("父标签")

    obj = None

    def validate_name(self, field):
        if Tag.query.filter(Tag.name == field.data).first():
            raise ValidationError("该标签名已存在! ")

    def validate_id(self, field):
        tag = Tag.query.filter(Tag.id == field.data).first()
        if not tag:
            raise ValidationError("找不到该标签! ")
        else:
            self.obj = tag

    def validate_parent_id(self, field):
        if not Tag.query.filter(Tag.id == field.data).first():
            raise ValidationError("父标签不存在! ")


class TagListForm(BaseForm):
    """查询标签列表"""
    page = IntegerField("页码", default=1, validators=[NumberRange(min=1, message="页码不能小于一")])


class VideoAddForm(BaseForm):
    """添加视频"""
    name = StringField("视频名", validators=[DataRequired("片名不能为空！")], )
    url = FileField("文件")
    info = TextAreaField("简介", validators=[DataRequired("简介不能为空！")])
    logo = FileField("封面")
    # user_id = IntegerField("所属用户", default=6666)
    # tag_id = SelectField("标签", coerce=int, choices="", default=18)


class VideoEditForm(BaseForm):
    """编辑视频"""
    id = StringField("id", validators=[DataRequired("视频id不能为空")])
    name = StringField("片名")
    url = FileField("文件")
    info = TextAreaField("简介")
    logo = FileField("封面")
    # tag_id = SelectField("标签", coerce=int, choices="")

    obj = None

    def validate_id(self, field):
        video = Video.query.filter(Video.id == field.data).first()
        if not video:
            raise ValidationError("找不到该视频! ")
        else:
            self.obj = video


class AnimationAddForm(BaseForm):
    tag_id = IntegerField("所属类别", default=0)  # 默认首页
    name = StringField("轮播图标题", validators=[DataRequired("NAME不能为空！")])
    logo = FileField("轮播图封面")
    url = StringField("轮播图指向的URL", validators=[DataRequired("URL不能为空！")])


class AnimationListForm(BaseForm):
    page = IntegerField("页码", default=1, validators=[NumberRange(min=1, message="页码不能小于一")])
    pagesize = IntegerField("数量", default=10, validators=[NumberRange(min=1, message="数量不能小于一")])
    q = StringField("搜索关键字")
    tag_id = IntegerField("标签或者分类或者分区", default=-1)


class AnimationEditForm(BaseForm):
    id = StringField("轮播图id", validators=[DataRequired("轮播图id不能为空")])
    name = StringField("轮播图标题")
    logo = FileField("轮播图封面")
    url = StringField("轮播图指向的URL")
    tag_id = IntegerField("所属类别")

    obj = None

    def validate_id(self, field):
        animation = Animation.query.filter(Animation.id == field.data).first()
        if not animation:
            raise ValidationError("找不到该轮播图! ")
        else:
            self.obj = animation


class AdminLogForm(BaseForm):
    page = IntegerField("页码", default=1, validators=[NumberRange(min=1, message="页码不能小于一")])


class MovieColSearchForm(BaseForm):
    q = StringField("搜索关键词", validators=[DataRequired("搜索关键词不能为空")])
    is_user = StringField("根据用户搜索", default=False)
    page = IntegerField("页码", default=1, validators=[NumberRange(min=1, message="页码不能小于一")])


class SearchOpLogForm(BaseForm):
    name = StringField("管理员名字")
    page = IntegerField("页码", default=1, validators=[NumberRange(min=1, message="页码不能小于一")])
    start_date = DateField("查询开始日期")
    end_date = DateField("查询结束日期", default=datetime.datetime.now)


class ListLoginLogForm(BaseForm):
    # 0为列出用户，1为列出管理员，-1为全部
    tag_id = IntegerField("tag_id", default=-1)
    page = IntegerField("页码", default=1, validators=[NumberRange(min=1, message="页码不能小于一")])


class SearchLoginLogForm(BaseForm):
    # 0为列出用户，1为列出管理员，-1为全部
    tag_id = IntegerField("tag_id", default=-1)
    page = IntegerField("页码", default=1, validators=[NumberRange(min=1, message="页码不能小于一")])
    name = StringField("管理员名字")
    start_date = DateField("查询开始日期")
    end_date = DateField("查询结束日期", default=datetime.datetime.now)


class SearchViewLogForm(BaseForm):
    page = IntegerField("页码", default=1, validators=[NumberRange(min=1, message="页码不能小于一")])
    name = StringField("用户名字")
    start_date = DateField("查询开始日期")
    end_date = DateField("查询结束日期", default=datetime.datetime.now)


class ListVideoForm(BaseForm):
    q = StringField("搜索关键字")
    tag_id = IntegerField("tag_id", default=-1)
    page = IntegerField("页码", default=1, validators=[NumberRange(min=1, message="页码不能小于一")])
    pagesize = IntegerField("数量", default=10, validators=[NumberRange(min=1, message="数量不能小于一")])


class ListUploadVideoForm(BaseForm):
    # 查看上传视频表，-1为全部，0为未审核，1为审核通过，2为审核不通过
    status = IntegerField("status", default=-1)
    page = IntegerField("页码", default=1, validators=[NumberRange(min=1, message="页码不能小于一")])
    pagesize = IntegerField("数量", default=10, validators=[NumberRange(min=1, message="数量不能小于一")])


class BangumiAddForm(BaseForm):
    name = StringField("番剧名", validators=[DataRequired("番剧名不能为空！")])
    info = TextAreaField("番剧简介", validators=[DataRequired("番剧简介不能为空！")])
    voice_actors = StringField("声优信息")
    staff = StringField("职员信息")
    logo = FileField("番剧封面")
    start_date = DateField("开播日期")
    update_time = TimeField("更新时间")
    update_weekday = IntegerField("更新日期（周几）")
    season = IntegerField("季度")
    area = StringField("地区", default="日本")
    # 1为国产 2为日漫 3为其他
    tag_id = IntegerField("类别（国产or日漫or其他）", default=2)


class BangumiListForm(BaseForm):
    # -1为全部 1为国产 2为日漫 3为其他
    tag_id = IntegerField("类别（日漫or国产or其他）", default=-1)
    page = IntegerField("页码", default=1, validators=[NumberRange(min=1, message="页码不能小于一")])


class BangumiEditForm(BaseForm):
    id = IntegerField("番剧ID", validators=[DataRequired("番剧ID不能为空！")])
    name = StringField("番剧名")
    info = TextAreaField("番剧简介")
    voice_actors = StringField("声优信息")
    staff = StringField("职员信息")
    logo = FileField("番剧封面")
    start_date = DateField("开播日期")
    update_time = TimeField("更新时间")
    update_weekday = IntegerField("更新日期（周几）")
    season = IntegerField("季度")
    area = StringField("地区")
    # 1为国产 2为日漫 3为其他
    tag_id = IntegerField("类别（日漫or国产or其他）")

    obj = None

    def validate_id(self, field):
        bangumi = Bangumi.query.filter(Bangumi.id == field.data).first()
        if not bangumi:
            raise ValidationError("找不到该番剧! ")
        else:
            self.obj = bangumi


class BangumiAddVideoForm(BaseForm):
    """番剧添加视频验证"""
    id = IntegerField("番剧ID", validators=[DataRequired("番剧ID不能为空！")])
    name = StringField("视频标题", validators=[DataRequired("视频标题不能为空！")])
    url = FileField("视频")
    logo = FileField("视频封面")
    is_finish = IntegerField("是否完结", default=0)

    obj = None

    def validate_id(self, field):
        bangumi = Bangumi.query.filter(Bangumi.id == field.data).first()
        if not bangumi:
            raise ValidationError("找不到该番剧! ")
        self.obj = bangumi
