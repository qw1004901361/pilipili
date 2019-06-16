# coding=UTF-8
import datetime

from sqlalchemy import Integer, String, Text, SmallInteger, ForeignKey, Date, DateTime, Sequence, \
    Time, Column, Float

from app.libs.enums import SeasonEnum, FinishEnum
from app.models.base import Base


class Tag(Base):
    """标签表"""
    __tablename__ = "tag"
    __table_args__ = {"extend_existing": True}

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 父标签
    parent_id = Column(Integer, default=None)
    # 标签名
    name = Column(String(100))
    # 简介
    info = Column(String(128))

    def __repr__(self):
        return "<Tag %r>" % self.name


class Animation(Base):
    """轮播图"""
    __tablename__ = "animation"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 轮播图名称
    name = Column(String(100))
    # 标签
    tag_id = Column(Integer)
    # 封面资源链接
    logo = Column(String(500))
    # 轮播图跳转链接
    url = Column(String(500))

    def __repr__(self):
        return "<Animation %r>" % self.name


class Comment(Base):
    """评论"""
    __tablename__ = "comment"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 评论的根节点
    root_id = Column(Integer, default=None)
    # 评论对象
    parent_id = Column(Integer, default=None)
    # 所属视频
    video_id = Column(Integer, ForeignKey('video.id'))
    # 所属用户
    user_id = Column(Integer, ForeignKey('user.id'))
    # 评论内容
    content = Column(Text)

    def __repr__(self):
        return "<Comment %r>" % self.id


class VideoCol(Base):
    """视频收藏"""
    __tablename__ = "videocol"
    __table_args__ = {"extend_existing": True}

    # 唯一ID标识，由uuid.uuid1()生成
    # id = Column(Integer, primary_key=True, autoincrement=True)
    # 所属视频
    video_id = Column(Integer, primary_key=True)
    # 所属用户
    user_id = Column(Integer, primary_key=True)

    def __repr__(self):
        return "<MovieCol %r>" % self.id


class Video(Base):
    """视频表"""
    __tablename__ = "video"
    __table_args__ = {"extend_existing": True}

    # 设置主键自动增长，从100开始
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 视频名
    name = Column(String(100))
    # 视频资源路径
    url = Column(String(255))
    # 简介
    info = Column(Text)
    # 封面资源路径
    logo = Column(String(255))
    # 播放量
    playnum = Column(Integer, default=0)
    # 评论量
    commentnum = Column(Integer, default=0)
    # 弹幕数
    danmunum = Column(Integer, default=0)
    # 收藏量
    colnum = Column(Integer, default=0)
    # 所属标签
    tag_id = Column(Integer)
    # 所属用户
    user_id = Column(Integer)
    # 播放时间
    release_time = Column(DateTime, default=datetime.datetime.now)
    # 播放时长，单位：秒
    length = Column(Integer)
    # 得分
    score = Column(Integer, default=0)

    def __repr__(self):
        return "<Video %r>" % self.name


class Piece(Base):
    """视频分p"""
    __tablename__ = "piece"
    __table_args__ = {"extend_existing": True}

    # 关联番剧ID，主键
    video_id = Column(Integer, primary_key=True)
    # 第几话
    piece = Column(Integer, primary_key=True)
    # 资源链接
    url = Column(String(255), nullable=False)


class Bangumi(Base):
    """番剧"""
    __tablename__ = "bangumi"
    __table_args__ = {"extend_existing": True}

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 番剧名
    name = Column(String(120))
    # 声优信息
    voice_actors = Column(String(500))
    # 职业信息
    staff = Column(String(500))
    # 总播放数
    playnum = Column(Integer, default=0)
    # 追番人数
    fannum = Column(Integer, default=0)
    # 评论总数
    commentnum = Column(Integer, default=0)
    # 弹幕总数
    danmunum = Column(Integer, default=0)
    # 收藏总数
    colnum = Column(Integer, default=0)
    # 综合评分
    score = Column(Integer)
    # 封面资源链接
    logo = Column(String(125))
    # 简介
    info = Column(String(500))
    # 开播日期（默认当前日期）
    start_date = Column(Date, default=datetime.datetime.now().date())
    # 更新时间（时：分）（默认当前时间）
    update_time = Column(Time, default=datetime.datetime.now().time().replace(second=0, microsecond=0))
    # 更新时间（星期几，1-7）（默认当前时间）
    update_weekday = Column(SmallInteger, default=datetime.datetime.now().isoweekday())
    # 集数
    episodes = Column(Integer)
    # 是否完结（默认连载中）
    is_finish = Column(SmallInteger, default=FinishEnum.UNFINISH.value)
    # 季节（默认春季新番）
    season = Column(SmallInteger, default=SeasonEnum.SPRING.value)
    # 地区（默认为日本）
    area = Column(String(100), default="日本")
    # 最新话
    new_piece = Column(SmallInteger, default=1)
    # 标签（日漫还是国产）
    tag_id = Column(Integer)
    # 用户点评分数
    grade = Column(Float)

    def __repr__(self):
        return "<Bangumi %r>" % self.name


class Episode(Base):
    """番剧分集"""
    __tablename__ = "episode"
    __table_args__ = {"extend_existing": True}

    # 关联番剧ID，主键
    bangumi_id = Column(Integer, primary_key=True)
    # 外键关联视频ID，主键
    video_id = Column(Integer, primary_key=True)
    # 第几话
    piece = Column(Integer)


class BangumiCol(Base):
    """番剧收藏（追番）"""
    __tablename__ = "bangumicol"
    __table_args__ = {"extend_existing": True}

    # id = Column(Integer, primary_key=True, autoincrement=True)
    # 所属番剧
    bangumi_id = Column(Integer, primary_key=True)
    # 所属用户
    user_id = Column(Integer, primary_key=True)

    def __repr__(self):
        return "<BangumiCol %r>" % self.id


class UploadVideo(Base):
    """用户上传视频表，审核通过后加到Video表中"""
    __tablename__ = "uploadvideo"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 视频名
    name = Column(String(100))
    # 视频资源路径
    url = Column(String(255))
    # 简介
    info = Column(Text)
    # 封面资源路径
    logo = Column(String(255))
    # 所属标签
    tag_id = Column(Integer)
    # 所属用户
    user_id = Column(Integer)
    # 上传时间
    upload_time = Column(DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return "<UploadVideo %r>" % self.name


class Verification(Base):
    """用户上传视频审核"""
    __tablename__ = "verification"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 视频id
    video_id = Column(Integer, ForeignKey("uploadvideo.id"), unique=True)
    # 审核状态，0为未审核，1为审核通过，2为审核不通过
    status = Column(SmallInteger, default=0)
    # 审核人
    admin_id = Column(Integer, default=None)

    def __repr__(self):
        return "<Verification %r>" % self.id
