# coding=UTF-8
import datetime


def write_oplog():
    """写入管理员操作记录"""
    from app.models.log import OpLog
    from app.models.base import db
    from flask_login import current_user
    from flask import request
    if current_user.is_authenticated:
        a = current_user.id
        with db.auto_commit():
            oplog = OpLog(admin_id=current_user.id,
                          ip=request.remote_addr, reason=request.method + " " + request.url)
            db.session.add(oplog)


def write_loginlog():
    """写入用户登录记录"""
    from app.models.log import LoginLog
    from app.models.base import db
    from flask_login import current_user
    from flask import request
    if current_user.is_authenticated:
        with db.auto_commit():
            loginlog = LoginLog(user_id=current_user.id, ip=request.remote_addr)
            db.session.add(loginlog)


def change_filename(filename):
    """修改文件名称"""
    import os
    import datetime
    import uuid
    fileinfo = os.path.splitext(filename)
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + \
               str(uuid.uuid4().hex) + fileinfo[-1]
    return filename


def make_dir():
    """判断是否存在目录，不存在则创建"""
    import os
    from flask import current_app
    if not os.path.exists(current_app.config["UP_DIR"]):
        os.makedirs(current_app.config["UP_DIR"])
        os.chmod(current_app.config["UP_DIR"], "rw")


def get_video_id():
    import uuid
    return uuid.uuid1().hex


class id_generator:
    """用于测试中主键的生成"""

    account = 0

    user_id = 0

    role_id = 0

    tag_id = 0

    video_id = 1000

    comment_id = 0

    col_id = 0

    @classmethod
    def get_account(cls):
        cls.account += 1
        return cls.account

    @classmethod
    def get_user_id(cls):
        cls.user_id += 1
        return cls.user_id

    @classmethod
    def get_role_id(cls):
        cls.role_id += 1
        return cls.role_id

    @classmethod
    def get_tag_id(cls):
        cls.tag_id += 1
        return cls.tag_id

    @classmethod
    def get_video_id(cls):
        cls.video_id += 1
        return cls.video_id

    @classmethod
    def get_comment_id(cls):
        cls.comment_id += 1
        return cls.comment_id

    @classmethod
    def get_col_id(cls):
        cls.col_id += 1
        return cls.col_id


import logging
from logging import handlers


def allowed_image_file(filename):
    from flask import current_app
    return '.' in filename and filename.rsplit('.', 1)[1] in current_app.config["IMAGE_ALLOWED_EXTENSIONS"]


def allowed_video_file(filename):
    from flask import current_app
    return '.' in filename and filename.rsplit('.', 1)[1] in current_app.config["VIDEO_ALLOWED_EXTENSIONS"]


class Logger(object):
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }  # 日志级别关系映射

    def __init__(self, filename, level='info', when='D', backCount=3,
                 fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'):
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)  # 设置日志格式
        self.logger.setLevel(self.level_relations.get(level))  # 设置日志级别
        sh = logging.StreamHandler()  # 往屏幕上输出
        sh.setFormatter(format_str)  # 设置屏幕上显示的格式
        th = handlers.TimedRotatingFileHandler(filename=filename, when=when, backupCount=backCount,
                                               encoding='utf-8')  # 往文件里写入指定间隔时间自动生成文件的处理器
        # 实例化TimedRotatingFileHandler
        # interval是时间间隔，backupCount是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位，单位有以下几种：
        # S 秒
        # M 分
        # H 小时、
        # D 天、
        # W 每星期（interval==0时代表星期一）
        # midnight 每天凌晨
        th.setFormatter(format_str)  # 设置文件里写入的格式
        self.logger.addHandler(sh)  # 把对象加到logger里
        self.logger.addHandler(th)


def num_assign(num):
    if num >= 100000000:
        return str(float('%.1f' % (num / 100000000))) + "亿"
    elif num >= 10000:
        return str(float('%.1f' % (num / 10000))) + "万"
    return str(num)


if __name__ == "__main__":
    print(get_video_id())
    print(datetime.datetime.now().date())
    print(datetime.datetime.now().time())
    print(datetime.datetime.now())
    print(datetime.datetime.now().isoweekday())
