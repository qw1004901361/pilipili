# coding=UTF-8
import uuid
from datetime import datetime

from flask_login import UserMixin
from flask_mail import text_type
from sqlalchemy import Integer, Column, String, Text, SmallInteger, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from app.libs.enums import GenderEnum
from app.models.base import Base


class BaseUser(Base, UserMixin):
    """基本用户信息表（管理员和普通用户）"""
    __tablename__ = "baseuser"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 名称
    name = Column(String(100), unique=True)
    # 性别
    gender = Column(SmallInteger, default=GenderEnum.UNKNOWN.value)
    # 账号
    account = Column(String(100), unique=True, nullable=False)
    # 密码
    _pwd = Column("pwd", String(128), nullable=False)

    @property
    def pwd(self):
        return self._pwd

    @pwd.setter
    def pwd(self, raw):
        """加密"""
        self._pwd = generate_password_hash(str(raw))

    def check_pwd(self, raw):
        # 验证密码
        return check_password_hash(self._pwd, str(raw))

    def __repr__(self):
        return '<BaseUser %r>' % self.name


# 会员数据模型
class User(Base):
    """用户表"""
    __tablename__ = "user"
    __table_args__ = {"extend_existing": True}

    # 外键关联baseuser.id，用户的拓展信息
    id = Column(Integer, ForeignKey('baseuser.id'), primary_key=True)
    # 用户除了可以注册账号，还可以使用通过关联邮箱，手机号码，登录
    # 邮箱
    email = Column(String(100), unique=True)
    # 手机号
    phone = Column(String(11), unique=True)
    # 个性简介
    info = Column(Text, default="这个人比较懒，没有留下任何信息╮(︶﹏︶)╭")
    # 头像
    face = Column(String(255))

    def __repr__(self):
        return '<User %r>' % self.id


# 管理员
class Admin(Base):
    """管理员表"""
    __tablename__ = "admin"
    __table_args__ = {"extend_existing": True}

    # 外键关联baseuser.id，管理员的拓展信息
    id = Column(Integer, ForeignKey('baseuser.id'), primary_key=True)
    # 登录次数
    login_counter = Column(Integer, default=0)

    def __repr__(self):
        return "<Admin %r>" % self.id


class UserRole(Base):
    """用户角色表"""
    __tablename__ = "user_role"
    __table_args__ = {"extend_existing": True}

    # 所属用户
    user_id = Column(Integer, primary_key=True)
    # 拥有的角色
    role_id = Column(Integer, primary_key=True)


class Role(Base):
    """角色表"""
    __tablename__ = "role"
    __table_args__ = {"extend_existing": True}

    # 唯一ID标识，由uuid.uuid1()生成
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 名称
    name = Column(String(100), unique=True)

    def __repr__(self):
        return "<Role %r>" % self.name


class RoleAuth(Base):
    """角色权限表"""
    __tablename__ = "role_auth"
    __table_args__ = {"extend_existing": True}

    # 所属角色
    role_id = Column(Integer, primary_key=True)
    # 拥有的权限
    auth_id = Column(Integer, primary_key=True)


class AuthModule(Base):
    """权限模块表"""
    __tablename__ = "authmodule"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 模块名字
    name = Column(String(20), unique=True)
    # 允许访问的模块
    module = Column(String(100))

    def __repr__(self):
        return "<AuthModule %r>" % self.name


class AuthApi(Base):
    """权限接口表（权限模块表下的细分）"""
    __tablename__ = "authapi"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 所属权限模块
    module_id = Column(Integer, ForeignKey('authmodule.id'))
    # 接口名字
    name = Column(String(20), unique=True)
    # 允许访问的接口
    api = Column(String(100))

    def __repr__(self):
        return "<AuthApi %r>" % self.name


class Follow(Base):
    """用户关注"""
    __tablename__ = "follow"
    __table_args__ = {"extend_existing": True}

    # 用户
    user_id = Column(Integer, primary_key=True)
    # 关注的人
    follow_id = Column(Integer, primary_key=True)

    def __repr__(self):
        return "<Follow %r>" % self.user_id
