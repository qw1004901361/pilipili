# coding=UTF-8
import re

from flask_login import current_user
from wtforms import Form, StringField, PasswordField, IntegerField, SelectMultipleField, SelectField
from wtforms.validators import DataRequired, ValidationError, Length, EqualTo

from app.forms.baseform import BaseForm
from app.models.video import Tag
from app.models.user import Admin, BaseUser, Role, AuthModule, AuthApi, User


class LoginForm(BaseForm):
    """登录"""
    account = StringField("账号", validators=[DataRequired("账号不能为空")])
    pwd = PasswordField("密码", validators=[DataRequired("密码不能为空")])

    obj = None

    type = None

    def validate_account(self, field):
        re_account = re.compile(r"^[a-zA-Z0-9]+$")
        re_email = re.compile(r"\w[-\w.+]*@([A-Za-z0-9][-A-Za-z0-9]+\.)+[A-Za-z]{2,14}")
        re_phone = re.compile(r"0?(13|14|15|18|17)[0-9]{9}")
        if re_account.match(field.data):
            baseuser = BaseUser.query.filter(BaseUser.account == field.data).first()
            self.obj = baseuser
        elif re_email.match(field.data):
            baseuser = BaseUser.query.join(User, User.id == BaseUser.id). \
                filter(User.user_email == field.data).first()
            self.obj = baseuser
        elif re_phone.match(field.data):
            baseuser = BaseUser.query.join(User, User.id == BaseUser.id). \
                filter(User.user_phone == field.data).first()
            self.obj = baseuser
        else:
            raise ValidationError("非法的帐号")


class PwdForm(BaseForm):
    """修改密码"""
    old_pwd = PasswordField("旧密码", validators=[DataRequired("旧密码不能为空")])
    new_pwd = PasswordField("新密码", validators=[DataRequired("新密码不能为空")])
    check_new_pwd = PasswordField("确认新密码", validators=[
        DataRequired("新密码不能为空"), EqualTo("new_pwd", message="两次输入密码不一致")])

    def validate_old_pwd(self, field):
        user = BaseUser.query.filter(BaseUser.id == current_user.id).first()
        if not user:
            raise ValidationError("错误，用户不存在")
        if not user.check_pwd(field.data):
            raise ValidationError("旧密码错误！")


class AuthModuleForm(BaseForm):
    name = StringField("模块名称", validators=[DataRequired("模块名称不能为空！")])
    module = StringField("允许访问的模块", validators=[DataRequired("模块不能为空！")])


class AuthModuleEditForm(BaseForm):
    id = StringField("模块ID", validators=[DataRequired(message="权限模块ID不能为空")])
    name = StringField("模块名称")
    module = StringField("允许访问的模块")

    obj = None

    def validate_id(self, field):
        authmodule = AuthModule.query.filter(AuthModule.id == field.data).first()
        if not authmodule:
            raise ValidationError("找不到该权限模块! ")
        else:
            self.obj = authmodule


class AuthApiForm(BaseForm):
    module_id = StringField("模块接口id", validators=[DataRequired("模块接口id不能为空！")])
    name = StringField("接口名称", validators=[DataRequired("接口名称不能为空！")])
    api = StringField("允许访问的接口", validators=[DataRequired("接口不能为空！")])

    def validate_id(self, field):
        if not AuthModule.query.filter(AuthModule.id == field.data).first():
            raise ValidationError("找不到该模块! ")


class AuthApiEditForm(BaseForm):
    id = StringField("权限接口id", validators=[DataRequired("权限接口id不能为空！")])
    module_id = StringField("权限模块id")
    name = StringField("权限名称")
    api = StringField("允许访问的接口")

    obj = None

    def validate_id(self, field):
        authapi = AuthApi.query.filter(AuthApi.id == field.data).first()
        if not authapi:
            raise ValidationError("找不到该权限! ")
        else:
            self.obj = authapi

    def validate_module_id(self, field):
        if not AuthModule.query.filter(AuthModule.id == field.data).first():
            raise ValidationError("找不到该模块! ")


class RoleAddForm(BaseForm):
    name = StringField("角色名称", validators=[DataRequired("角色名称不能为空！")])
    # 权限多选框
    auths = SelectMultipleField("权限列表", validators=[DataRequired("权限列表不能为空！")],
                                coerce=int,
                                choices="")


class RoleEditForm(BaseForm):
    id = StringField("角色id", validators=[DataRequired("角色id不能为空！")])
    name = StringField("角色名称")
    # 多选框
    auths = SelectMultipleField("权限列表", coerce=int, choices="")

    obj = None

    def validate_id(self, field):
        role = Role.query.filter(Role.id == field.data).first()
        if not role:
            raise ValidationError("找不到该角色! ")
        else:
            self.obj = role

    def validate_name(self, field):
        if Role.query.filter(Role.name == field.data).first():
            raise ValidationError("角色名称已存在")
