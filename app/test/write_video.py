# coding=UTF-8
import datetime
import os, shutil
import time
import uuid

from moviepy.video.io.VideoFileClip import VideoFileClip
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json

from werkzeug.utils import secure_filename

from app.libs.enums import GenderEnum
from app.libs.utils import id_generator, change_filename
from app.models.user import BaseUser, User, UserRole

from app.models.video import Video, Tag

session = None


def init():
    """连接数据库"""
    engine = create_engine("mysql+pymysql://root:qw971230@localhost:3306/pilipili")
    Session = sessionmaker(bind=engine)
    global session
    session = Session()

    for i in session.query(User).all():
        session.delete(i)


def add_user(user_name, user_face):
    """生成用户"""
    # 基本用户
    try:
        baseuser = BaseUser()
        baseuser.name = user_name
        baseuser.gender = GenderEnum.UNKNOWN.value,
        baseuser.account = baseuser.id
        baseuser.pwd = baseuser.id
        session.add(baseuser)
        session.commit()
    except Exception:
        session.rollback()
    baseuser = session.query(BaseUser).filter(BaseUser.name == user_name).first()
    # 用户额外信息
    try:
        user = User()
        user.id = baseuser.id
        user.face = user_face
        session.add(user)
        session.commit()
    except Exception:
        session.rollback()
    # 用户角色赋予
    try:
        session.add(UserRole(user_id=baseuser.id, role_id=1))
        session.commit()
    except Exception:
        session.rollback()
    return baseuser


def change_video(video_path):
    """视频转换"""
    if os.path.isfile(video_path):
        a = os.path.dirname(__file__)
        b = os.path.dirname(a)
        c = os.path.abspath(b)
        dir = os.path.join(c, 'static', 'video')
        new_name = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + ".flv"
        new_path = os.path.join(dir, new_name)
        shutil.copy(video_path, new_path)
        # url = "/static/video/" + new_name
        return new_name
    return None


def generate_video(user_id, data, video_path):
    """生成视频"""
    video = session.query(Video).filter(Video.name == data["name"]).first()
    if video:
        return video
    try:
        video = Video()
        video.id = id_generator.get_video_id()
        video.name = data["name"]
        video.info = data["info"]
        video.logo = data["logo"]
        video.user_id = user_id
        try:
            video_clip = VideoFileClip(video_path)
            video.length = video_clip.duration
            video_clip.reader.close()
            video_clip.audio.reader.close_proc()
        except Exception as e:
            video.length = None
        video.url = change_video(video_path)
        tag = session.query(Tag).filter(Tag.name == data["tag"]).first()
        if tag:
            video.tag_id = tag.id
        video.playnum = data["playnum"]
        video.commentnum = data["commentnum"]
        video.colnum = data["colnum"]
        video.release_time = datetime.datetime.fromtimestamp(data["release_time"])
        session.add(video)
        session.commit()
    except Exception as e:
        print(e)
        print("添加视频信息失败")
        session.rollback()
    return video


def write_data():
    """将爬取的数据写入数据库"""
    a = os.path.dirname(__file__)
    b = os.path.dirname(a)
    c = os.path.abspath(b)
    rootdir = os.path.join(c, 'static', 'bilibili_video')
    dir_list = os.listdir(rootdir)
    print("转换数量为：" + str(len(dir_list)), end="\n")
    for i in range(0, len(dir_list)):
        print("开始第{}个".format(i + 1))
        sub_dir = os.path.join(rootdir, dir_list[i])
        print(sub_dir + "——》开始转换")
        video_path = os.path.join(sub_dir, sub_dir.replace(rootdir + "\\", "") + ".flv")
        with open(os.path.join(sub_dir, "detail.json"), encoding="utf-8") as f:
            data = json.load(f)
            baseuser = add_user(user_name=data["user"], user_face=data["user_face"])
            video = generate_video(user_id=baseuser.id, data=data, video_path=video_path)
        print(sub_dir + "——》转换完成", end="\n")


if __name__ == "__main__":
    init()
    write_data()
