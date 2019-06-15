# coding=UTF-8
import os, stat

from flasgger import Swagger
from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
# from flask_redis import FlaskRedis
from werkzeug.exceptions import HTTPException

from app.api.admin import create_admin_blueprint
from app.api.home import create_home_blueprint
from app.libs.enums import ReturnEnum
from app.libs.error import APIException
from app.libs.error_code import ServerError
from app.libs.task import calculate_avg_score
from app.libs.utils import make_dir
from app.models.base import db
from app.models.user import BaseUser
from app.view_models.return_obj import ReturnObj
from flask_apscheduler import APScheduler

import logging

login_manager = LoginManager()

# rd = FlaskRedis()

swagger = Swagger()


def create_app():
    # 实例化Flask核心对象
    app = Flask(__name__)

    # # 设置日志
    # logging.basicConfig(level=logging.DEBUG,  # 控制台打印的日志级别
    #                     filename='app/log/error_log.log',
    #                     filemode='a',  # 模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
    #                     # a是追加模式，默认如果不写的话，就是追加模式
    #                     format=
    #                     '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
    #                     # 日志格式
    #                     )

    # flasgger初始化
    swagger.init_app(app)

    # 加载配置文件
    app.config.from_object("app.config.setting")
    app.config.from_object("app.config.secure")

    # 生成视频文件储存位置
    if not os.path.exists(app.config["VIDEO_DIR"]):
        os.makedirs(app.config["VIDEO_DIR"])
        os.chmod(app.config["VIDEO_DIR"], stat.S_IRWXU)

    # 生成视频封面文件储存位置
    if not os.path.exists(app.config["LOGO_DIR"]):
        os.makedirs(app.config["LOGO_DIR"])
        os.chmod(app.config["LOGO_DIR"], stat.S_IRWXU)

    # 生成用户头像文件储存位置
    if not os.path.exists(app.config["FACE_DIR"]):
        os.makedirs(app.config["FACE_DIR"])
        os.chmod(app.config["FACE_DIR"], stat.S_IRWXU)

    # 数据库初始化
    db.init_app(app)
    db.create_all(app=app)

    # redis初始化
    # rd.init_app(app=app)

    # 注册蓝图
    app.register_blueprint(create_admin_blueprint())
    app.register_blueprint(create_home_blueprint())

    # 登录插件flask_login初始化
    login_manager.init_app(app)

    # 设置登录视图函数
    # login_manager.login_view = "home.login"
    # 设置提示信息
    # login_manager.login_message = "请登录或注册"

    # login_manager所需，自动调用
    @login_manager.user_loader
    def get_user(id):
        return BaseUser.query.get(id)

    # @login_manager.unauthorized_handler装饰器所修饰的方法就会代替”@login_required”装饰器的默认处理方法。
    # 设置后，登陆视图函数和提示信息无效
    @login_manager.unauthorized_handler
    def unauthorized_handler():
        return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "请登录")

    # 全局异常处理
    @app.errorhandler(Exception)
    def framework_error(e):
        if isinstance(e, APIException):
            return e
        if isinstance(e, HTTPException):
            code = e.code
            msg = e.description
            error_code = 1007
            return APIException(msg, code, error_code)
        else:
            # 系统错误，记录日志
            # logging.error(e.args)
            raise e
            # return APIException(msg=str(e), code=500)
            # return ServerError()

    # 注册APScheduler
    scheduler = APScheduler()
    scheduler.init_app(app=app)
    # 添加作业
    scheduler.add_job(func=calculate_avg_score, id="tasks-score", trigger="interval", seconds=1 * 60 * 60)
    scheduler.start()

    # 跨域
    CORS(app, supports_credentials=True)

    return app
