# coding=UTF-8
import datetime

from flasgger import swag_from
from flask import request
from flask_login import login_user, current_user, logout_user

from app.forms.auth import LoginForm
from app.forms.user import UserAddForm
from app.libs.auth import load_auth
from app.libs.enums import ReturnEnum
from app.libs.redprint import Redprint
from app.models.base import db
from app.models.log import LoginLog
from app.models.user import BaseUser, User, UserRole, Role
from app.view_models.return_obj import ReturnObj

base = Redprint("base")


@base.route("/login", methods=["POST"])
# @swag_from("../../yml/admin/base/user_login.yml")
def login():
    """登录"""
    form = LoginForm().validate_for_api()
    baseuser = form.obj
    if baseuser and baseuser.check_pwd(form.pwd.data):
        # 第三方插件实现写入cookie
        continued_time = datetime.timedelta(hours=2)  # cookie有效时间
        # 将当前用户的信息写入session
        login_user(baseuser, remember=True, duration=continued_time)
        # 加载当前用户的权限，写入session
        load_auth()
        with db.auto_commit():
            # 记录用户登录记录
            loginlog = LoginLog(user_id=current_user.id, ip=request.remote_addr)
            db.session.add(loginlog)
        return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")
    return ReturnObj.get_response(ReturnEnum.LOGIN_ERROR.value, "帐号不存在或密码错误")


@base.route("/logout")
def logout():
    """退出登录"""
    # 从session中清除当前用户的信息
    logout_user()
    # 清空session
    # session.clear
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")


@base.route("/register", methods=["POST"])
def register():
    """注册"""
    form = UserAddForm().validate_for_api()
    try:
        with db.auto_commit():
            # 基本用户
            baseuser = BaseUser()
            baseuser.name = form.name.data
            baseuser.account = form.account.data
            baseuser.pwd = form.pwd.data
            db.session.add(baseuser)
    except Exception as e:
        print(e)
        return ReturnObj.get_response(ReturnEnum.ADD_BASEUSER_FAIL.value, "添加用户基本信息失败")
    baseuser = BaseUser.query.filter(BaseUser.account == form.account.data).first()
    try:
        with db.auto_commit():
            # 用户其他信息
            user = User()
            user.id = baseuser.id
            db.session.add(user)
    except Exception as e:
        print(e)
        return ReturnObj.get_response(ReturnEnum.ADD_USER_FAIL.value, "添加用户额外信息失败")
    try:
        with db.auto_commit():
            # 赋予用户相应角色
            user_role = UserRole()
            user_role.user_id = baseuser.id
            user_role.role_id = Role.query.filter(Role.name == "普通用户").first().id
            db.session.add(user_role)
    except Exception as e:
        print(e)
        return ReturnObj.get_response(ReturnEnum.ADD_USERROLE_FAIL.value, "赋予用户角色失败")
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")


@base.route("/is_login")
def is_login():
    """判断当前用户是否登录"""
    if current_user.is_authenticated:
        user = User.query.filter(User.id == current_user.id).first()
        r = {
            "name": current_user.name,
            "face": user.face if user else None
        }
        return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "ok", data=r)
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "cancel")

# @base.route("/tm", methods=["GET", "POST"])
# def tm():
#     """弹幕消息处理"""
#     from app import rd
#     if request.method == "GET":
#         # 获取弹幕消息队列
#         id = request.args.get('id')
#         # 存放在redis队列中的键值
#         key = "video" + str(id)
#         if rd.llen(key):
#             msgs = rd.lrange(key, 0, 2999)
#             res = {
#                 "code": 1,
#                 "danmaku": [jsonify(v) for v in msgs]
#             }
#         else:
#             res = {
#                 "code": 1,
#                 "danmaku": []
#             }
#         resp = jsonify(res)
#     if request.method == "POST":
#         # 添加弹幕
#         data = jsonify(request.get_data())
#         msg = {
#             "__v": 0,
#             "author": data["author"],
#             "time": data["time"],
#             "text": data["text"],
#             "color": data["color"],
#             "type": data['type'],
#             "ip": request.remote_addr,
#             "_id": datetime.datetime.now().strftime("%Y%m%d%H%M%S") + uuid.uuid4().hex,
#             "player": [
#                 data["player"]
#             ]
#         }
#         res = {
#             "code": 1,
#             "data": msg
#         }
#         resp = jsonify(res)
#         # 将添加的弹幕推入redis的队列中
#         rd.lpush("video" + str(data["player"]), jsonify(msg))
#     return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=resp)
