# coding=UTF-8
from enum import Enum


class GenderEnum(Enum):
    # 未知
    UNKNOWN = 0
    # 男性
    MALE = 1
    # 女性
    FEMALE = 2


class WeekEnum(Enum):
    MON = 1
    TUES = 2
    WED = 3
    THUR = 4
    FRI = 5
    SAT = 6
    SUN = 7


class FinishEnum(Enum):
    # 连载
    UNFINISH = 0
    # 完结
    FINISH = 1


class SeasonEnum(Enum):
    # 春天（一月新番）
    SPRING = 1
    # 夏天（四月新番）
    SUMMER = 2
    # 秋天（七月新番）
    AUTUMN = 3
    # 冬天（十月新番）
    WINTER = 4


class ReturnEnum(Enum):
    # 请求成功
    SUCCESS = 1000
    # 请求失败
    FAIL = 9999
    # 找不到该资源
    NOT_FOUND = 404

    # 具体原因
    # 用户相关
    ADD_BASEUSER_FAIL = 1001  # 添加baseuser失败
    ADD_USER_FAIL = 1002  # 添加user失败
    ADD_ADMIN_FAIL = 1003  # 添加admin失败
    ADD_USERROLE_FAIL = 1004  # 添加userrole失败
    LOGIN_ERROR = 1005  # 帐号不存在或密码错误
    ADMIN_DEL_ERROR = 1006  # 该用户也是管理员，不能删除
    # 视频相关
    UPLOAD_ANIMATION_LOGO = 2001  # 没有上传轮播图封面
    IMAGE_TYPE_ERROR = 2002  # 只允许上传png jpg jpeg gif格式
    VIDEO_TYPE_ERROR = 2003  # 只允许上传mp4 avi flv wmv格式
    UPLOAD_VIDEO_LOGO = 2004  # 没有上传视频封面
    UPLOAD_VIDEO = 2005  # 没有上传视频
    UPLOADVIDE0_NOT_EXIST = 2006  # 上传视频不存在
    ADD_UPLOADVIDE0_ERROR = 2007  # 上传视频失败
    ADD_VERIFICATION_ERROR = 2008  # 添加审核状态失败
    # 验证
    WTFORMS_FAIL = 4000  # wtforms验证不通过
