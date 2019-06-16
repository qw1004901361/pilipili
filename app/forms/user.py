# coding=UTF-8
import re

from flask_login import current_user
from wtforms import StringField, PasswordField, SelectField, TextAreaField, FileField, SelectMultipleField, IntegerField
from wtforms.validators import DataRequired, ValidationError, Email, Regexp, Optional

from app.forms.baseform import BaseForm
from app.libs.enums import GenderEnum, ReturnEnum
from app.models.user import BaseUser, Admin, User
from app.view_models.return_obj import ReturnObj


class AdminAddForm(BaseForm):
    """超级管理员添加管理员"""
    account = StringField("账号", validators=[DataRequired("账号不能为空")])
    pwd = PasswordField("密码", default="123456")
    name = StringField("名字", default="管理员")
    gender = IntegerField("性别", default=1)
    role_id = SelectMultipleField("所属角色", coerce=int, choices="")

    def validate_account(self, field):
        user = BaseUser.query.filter(BaseUser.account == field.data).first()
        if user:
            raise ValidationError("帐号已经存在！")


class AdminEditForm(BaseForm):
    """管理员修改个人信息"""
    name = StringField("名字")
    gender = StringField("性别")

    def validate_name(self, field):
        baseuser = BaseUser.query.filter(BaseUser.name == field.data).first()
        if baseuser:
            if self.obj == baseuser:
                pass
            else:
                raise ValidationError("该名字已被使用！")

    def validate_gender(self, field):
        if field.data:
            try:
                GenderEnum(int(field.data))
            except ValueError:
                raise ValidationError("性别错误")


class SuperAdminEditForm(BaseForm):
    """超级管理员修改管理员信息（赋予新的角色等）"""
    id = StringField("管理员id", validators=[DataRequired("管理员id不能为空！")])
    pwd = PasswordField("密码")
    name = StringField("名字")
    gender = StringField("性别")
    role_id = SelectMultipleField("所属角色", coerce=int, choices="")

    obj = None

    def validate_id(self, field):
        admin = Admin.query.filter(Admin.id == field.data).first()
        if not admin:
            raise ValidationError("找不到该管理员! ")
        baseuser = BaseUser.query.filter(BaseUser.id == admin.id).first()
        self.obj = baseuser

    def validate_name(self, field):
        baseuser = BaseUser.query.filter(BaseUser.name == field.data).first()
        if baseuser:
            if self.obj == baseuser:
                pass
            else:
                raise ValidationError("该名称已被使用")


class UserAddForm(BaseForm):
    """用户注册"""
    account = StringField("账号", validators=[DataRequired("账号不能为空")])
    pwd = PasswordField("密码", validators=[DataRequired("密码不能为空")])
    name = StringField("名字", validators=[DataRequired("名称不能为空")])

    def validate_account(self, field):
        # re_account = re.compile(r"^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d]{6,14}$")
        # if not re_account.match(field.data):
        #     raise ValidationError("非法的帐号，帐号只含有英文和数字，且长度为6-14位")
        if BaseUser.query.filter(BaseUser.account == field.data).first():
            raise ValidationError("该账号已被注册")

    def validate_name(self, field):
        user = BaseUser.query.filter(BaseUser.name == field.data).first()
        if user:
            raise ValidationError("该名称已被使用")


class UserEditForm(BaseForm):
    """用户修改个人信息"""
    id = StringField("用户id")
    name = StringField("名字", validators=[Optional()])
    gender = StringField("性别", validators=[Optional()])
    email = StringField("用户邮箱", validators=[Optional(), Email(message="非法的电子邮箱")])
    phone = StringField("用户电话号码", validators=[Optional(), Regexp(r"0?(13|14|15|18|17)[0-9]{9}", message="非法的手机号码")])
    info = TextAreaField("用户简介", validators=[Optional()])
    face = FileField("用户头像", validators=[Optional()])

    obj = None

    def validate_id(self, field):
        baseuser = BaseUser.query.filter(BaseUser.id == current_user.id).first()
        if not baseuser:
            raise ValidationError("找不到该用户")
        else:
            self.obj = baseuser

    def validate_name(self, field):
        user = BaseUser.query.filter(BaseUser.name == field.data).first()
        if user:
            raise ValidationError("该名称已被使用")

    def validate_gender(self, field):
        try:
            GenderEnum(int(field.data))
        except ValueError:
            raise ValidationError("性别错误")

    def validate_email(self, field):
        user = User.query.filter(User.email == field.data).first()
        if user:
            raise ValidationError("该邮箱已被使用")

    def validate_phone(self, field):
        user = User.query.filter(User.phone == field.data).first()
        if user:
            raise ValidationError("该电话号码已被使用")


class AdminAddUserForm(BaseForm):
    """管理员添加新的用户"""
    name = StringField("名字", validators=[DataRequired("名字不能为空！")])
    account = StringField("帐号", validators=[DataRequired("帐号不能为空！")])
    pwd = StringField("密码", default="pilipili")
    gender = StringField("性别", default=0)
    email = StringField("邮箱", validators=[Optional(), Email("非法的电子邮箱")])
    phone = StringField("电话号码", validators=[Optional(), Regexp(r"0?(13|14|15|18|17)[0-9]{9}", message="非法的手机号码")])
    info = StringField("用户简介")
    face = FileField("用户头像")

    def validate_account(self, field):
        # 帐号值只含有英文和数字
        # re_account = re.compile(r"^[a-zA-Z0-9]+$")
        # if not re_account.match(field.data):
        #     raise ValidationError("非法的帐号，帐号只含有英文字母和阿拉伯数字")
        if BaseUser.query.filter(BaseUser.account == field.data).first():
            raise ValidationError("该账号已被注册")

    def validate_name(self, field):
        user = BaseUser.query.filter(BaseUser.name == field.data).first()
        if user:
            raise ValidationError("该名称已被使用")

    def validate_email(self, field):
        user = User.query.filter(User.email == field.data).first()
        if user:
            raise ValidationError("该邮箱已被使用")

    def validate_phone(self, field):
        user = User.query.filter(User.phone == field.data).first()
        if user:
            raise ValidationError("该电话号码已被使用")

    def validate_gender(self, field):
        if field.data:
            try:
                GenderEnum(int(field.data))
            except ValueError:
                raise ValidationError("性别错误")


class AdminEditUserForm(BaseForm):
    """管理员修改用户信息"""
    id = StringField("用户ID", validators=[DataRequired("用户ID不能为空")])
    name = StringField("名字")
    # 帐号只含有英文和数字
    gender = StringField("性别")
    pwd = StringField("密码")
    email = StringField("邮箱", validators=[Optional(), Email("非法的电子邮箱")])
    phone = StringField("电话号码", validators=[Optional(), Regexp(r"0?(13|14|15|18|17)[0-9]{9}", message="非法的手机号码")])
    info = StringField("用户简介")
    face = FileField("用户头像")

    obj = None

    def validate_id(self, field):
        baseuser = BaseUser.query.filter(BaseUser.id == field.data).first()
        if not baseuser:
            raise ValidationError("找不到该用户")
        admin = Admin.query.filter(Admin.id == baseuser.id).first()
        if admin:
            raise ValidationError("没有权限修改管理员信息")
        self.obj = baseuser

    def validate_name(self, field):
        user = BaseUser.query.filter(BaseUser.name == field.data).first()
        if user:
            if self.obj == user:
                pass
            else:
                raise ValidationError("该名称已被使用")

    def validate_email(self, field):
        user = User.query.filter(User.email == field.data).first()
        if user:
            if self.obj == user:
                pass
            else:
                raise ValidationError("该邮箱已被使用")

    def validate_phone(self, field):
        user = User.query.filter(User.phone == field.data).first()
        if user:
            if self.obj == user:
                pass
            else:
                raise ValidationError("该电话号码已被使用")

    def validate_gender(self, field):
        if field.data:
            try:
                GenderEnum(int(field.data))
            except ValueError:
                raise ValidationError("性别错误")


class FanOrFollowForm(BaseForm):
    # 查找粉丝或者关注
    tag_id = SelectField("tag_id", coerce=int, choices=[(1, "fan"), (2, "follow")], default=1)


class CancelColForm(BaseForm):
    # 取消收藏验证
    id = SelectMultipleField("col_id", coerce=int, choices="")
