# coding=UTF-8
import os

# 每页标签数
PER_TAG_PAGE = 5
# 每页视频数
PER_PAGE = 10
# 每页评论数
PER_COM_PAGE = 20
# 视频存放目录
VIDEO_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../static/video/")
# 视频封面存在目录
LOGO_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../static/logo/")
# 用户头像存放目录
FACE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../static/face/")
# 临时目录
TMP_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../static/tmp/")
# 支持返回中文
JSON_AS_ASCII = False
# 允许图片扩展名
IMAGE_ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']
# 允许视频扩展名
VIDEO_ALLOWED_EXTENSIONS = ['mp4', 'avi', 'flv', 'wmv']

# 管理员界面每页评论数
ADMIN_PER_COM_PAGE = 10
# 管理员界面每页轮播图数
ADMIN_PER_ANI_PAGE = 10
# 管理员界面每页日志数
ADMIN_PER_LOG_PAGE = 10
# 管理员界面每页角色数
ADMIN_PER_ROLE_PAGE = 10
# 管理员界面每页用户数
ADMIN_PER_USER_PAGE = 10
# 管理员界面每页视频数
ADMIN_PER_VIDEO_PAGE = 10
# 管理员界面每页模块数
ADMIN_PER_MODULE_PAGE = 10
# 管理严界面每页标签数
ADMIN_PER_TAG_PAGE = 10

path = "http://localhost:5000/"
# video资源路径
VIDEO_PATH = path + "static/video/"
# logo资源路径
LOGO_PATH = path + "static/logo/"
# face资源路径
FACE_PATH = path + "static/face/"
# tmp资源路径
TMP_PATH = path + "static/tmp/"
