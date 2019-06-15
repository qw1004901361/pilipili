# coding=UTF-8
import datetime
import os, shutil
import uuid

from moviepy.video.io.VideoFileClip import VideoFileClip
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json

from app.libs.enums import GenderEnum, SeasonEnum
from app.libs.utils import id_generator
from app.models.user import BaseUser, User, UserRole

from app.models.video import Video, Tag, Bangumi, Episode

session = None


def init():
    """连接数据库"""
    engine = create_engine("mysql+pymysql://root:qw971230@localhost:3306/pilipili")
    Session = sessionmaker(bind=engine)
    global session
    session = Session()

    for i in session.query(User).all():
        session.delete(i)


def generate_user():
    """生成用户"""
    baseuser = session.query(BaseUser).filter(BaseUser.id == 6666).first()
    if baseuser:
        return baseuser
    try:
        # 基本用户
        baseuser = BaseUser()
        baseuser.id = 6666
        baseuser.name = "pilipili番剧"
        baseuser.gender = GenderEnum.UNKNOWN.value,
        baseuser.account = 6666
        baseuser.pwd = baseuser.account
        session.add(baseuser)
        session.commit()
        # 用户额外信息
        user = User()
        user.id = baseuser.id
        user.face = "i2.hdslb.com/bfs/face/60a9153609998b04301dc5b8ed44c41b537a2268.jpg"
        session.add(user)
        session.commit()
        # 用户角色赋予
        session.add(UserRole(user_id=baseuser.id, role_id=1))
        session.commit()
    except Exception as e:
        print(e)
        print("添加用户信息失败")
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
        return new_name
    return None


def generate_video(user_id, data, video_path):
    """生成视频"""
    video = None
    try:
        video = Video()
        # video.id = id_generator.get_video_id()
        video.name = data["name"]
        # video.info = data["info"]
        video.logo = data["logo"]
        video.user_id = user_id
        try:
            video_clip = VideoFileClip(video_path)
            video.length = video_clip.duration
            video_clip.reader.close()
            video_clip.audio.reader.close_proc()
        except Exception as e:
            print(e)
            video.length = None
        video.url = change_video(video_path)
        # video.tag_id = 19 if is_finish == 1 else 18
        # video.playnum = data["playnum"]
        video.commentnum = data["commentnum"]
        # video.colnum = data["colnum"]
        video.release_time = datetime.datetime.strptime(data["pub_time"], "%Y-%m-%d %H:%M:%S")
        session.add(video)
        session.commit()
    except Exception as e:
        print(e)
        print("添加视频信息失败")
        session.rollback()
    return video


def generate_bangumi(data):
    bangumi = session.query(Bangumi).filter(Bangumi.name == data["name"]).first()
    if bangumi:
        return bangumi
    try:
        bangumi = Bangumi()
        # bangumi.id = id_generator.get_video_id()
        bangumi.name = data["name"]
        bangumi.voice_actors = data["voice_actors"]
        bangumi.staff = data["staff"]
        bangumi.playnum = data["playnum"]
        bangumi.fannum = data["fannum"]
        bangumi.danmunum = data["danmunum"]
        bangumi.score = data["score"]
        bangumi.info = data["info"]
        bangumi.logo = data["logo"]
        bangumi.start_date = datetime.datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        bangumi.update_time = datetime.datetime.strptime(data["update_time"], "%Y-%m-%d %H:%M:%S").time()
        bangumi.update_weekday = datetime.datetime.strptime(data["update_time"], "%Y-%m-%d %H:%M:%S").isoweekday()
        bangumi.episodes = data["episodes"]["total"]
        bangumi.is_finish = data["is_end"]
        tmp = bangumi.start_date.month
        if tmp <= 3:
            bangumi.season = SeasonEnum.SPRING.value
        elif tmp <= 6:
            bangumi.season = SeasonEnum.SUMMER.value
        elif tmp <= 9:
            bangumi.season = SeasonEnum.AUTUMN.value
        else:
            bangumi.season = SeasonEnum.WINTER.value
        session.add(bangumi)
        session.commit()
    except Exception as e:
        print(e)
        print("添加视频信息失败")
        session.rollback()
    return bangumi


def generate_episode(video_id, bangumi_id, piece):
    try:
        episode = Episode()
        episode.video_id = video_id
        episode.bangumi_id = bangumi_id
        episode.piece = piece
        session.add(episode)
        # session.commit()
    except Exception as e:
        print(e)
        print("添加视频信息失败")
        session.rollback()


def write_data():
    """将爬取的数据写入数据库"""
    init()
    c = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    rootdir = os.path.join(c, 'static', 'bangumi')
    dir_list = os.listdir(rootdir)
    print("转换数量为：" + str(len(dir_list)), end="\n")
    for i in range(0, len(dir_list)):
        print("开始第{}个".format(i + 1))
        sub_dir = os.path.join(rootdir, dir_list[i])
        print("转换开始")
        with open(os.path.join(sub_dir, "detail.json"), encoding="utf-8") as f:
            data = json.load(f)
        baseuser = generate_user()
        bangumi = generate_bangumi(data)
        for j in data["episodes"]["episodes"]:
            video_path = os.path.join(sub_dir, str(j["piece"]) + ".mp4")
            print(video_path + "——》开始转换")
            if not os.path.exists(video_path):
                continue
            video = generate_video(user_id=baseuser.id, data=j, video_path=video_path)
            generate_episode(video.id, bangumi.id, j["piece"])
            print(video_path + "——》转换完成", end="\n")
        print("转换结束", end="\n")


def update_season():
    engine = create_engine("mysql+pymysql://root:qw971230@localhost:3306/pilipili")
    Session = sessionmaker(bind=engine)
    session = Session()
    for i in session.query(Bangumi).all():
        tmp = i.start_date.month
        if tmp <= 3:
            i.season = SeasonEnum.SPRING.value
        elif tmp <= 6:
            i.season = SeasonEnum.SUMMER.value
        elif tmp <= 9:
            i.season = SeasonEnum.AUTUMN.value
        else:
            i.season = SeasonEnum.WINTER.value
        session.add(i)
    session.commit()


if __name__ == "__main__":
    write_data()
    # update_season()
