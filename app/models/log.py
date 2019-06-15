# coding=UTF-8
import datetime

from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, func
from sqlalchemy.orm import relationship

from app.models.base import Base


class LoginLog(Base):
    """登录日志表"""
    __tablename__ = "loginlog"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    # ip地址
    ip = Column(String(100))
    # 所属用户
    user_id = Column(Integer)
    # 详细地点
    location = Column(String(100))

    def __repr__(self):
        return '<LoginLog %r>' % self.id


class ViewLog(Base):
    """观看日志表"""
    __tablename__ = "viewlog"
    __table_args__ = {"extend_existing": True}

    # 所属用户
    user_id = Column(Integer, primary_key=True)
    # 观看视频
    video_id = Column(Integer, primary_key=True)
    # 更新时间
    update_time = Column(DateTime, default=datetime.datetime.now)


class OpLog(Base):
    """管理员操作日志表"""
    __tablename__ = "oplog"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    # 所属管理员
    admin_id = Column(Integer)
    # 操作IP
    ip = Column(String(100))
    # 操作原因
    reason = Column(String(600))

    def __repr__(self):
        return "<Oplog %r>" % self.id
