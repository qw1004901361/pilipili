# coding=UTF-8
import datetime
import json
import os
import random
import re

import requests
from lxml import etree
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.utils import secure_filename

from app.libs.enums import GenderEnum
from app.models.user import BaseUser, User, UserRole
from app.models.video import Animation, Video, Tag


def get_recommend():
    # 连接数据库
    engine = create_engine("mysql+pymysql://root:qw971230@localhost:3306/pilipili")
    Session = sessionmaker(bind=engine)
    session = Session()
    # 获取推荐
    url = 'https://www.bilibili.com'
    recommend_list = []
    html = requests.get(url=url)
    selector = etree.HTML(html.text)
    href_content = selector.xpath(
        "//div[@id='app']/div[@class='bili-wrapper']/div[@id='chief_recommend']/div[@class='carousel-box']/div[@class='carousel-module']/div[@class='panel']/ul[@class='pic']/li/a[1]/@href"
    )
    img_content = selector.xpath(
        "//div[@id='app']/div[@class='bili-wrapper']/div[@id='chief_recommend']/div[@class='carousel-box']/div[@class='carousel-module']/div[@class='panel']/ul[@class='pic']/li/a[1]/img/@src")
    name_content = selector.xpath(
        "//div[@id='app']/div[@class='bili-wrapper']/div[@id='chief_recommend']/div[@class='carousel-box']/div[@class='carousel-module']/div[@class='panel']/ul[@class='title']/a/text()"
    )
    for i, j, k in zip(href_content, img_content, name_content):
        animation = Animation()
        animation.name = k.replace("\n", "").replace(" ", "")
        animation.logo = "https://" + j.replace("https://", "").replace("//", "")
        animation.url = "https://" + i.replace("https://", "")
        recommend_list.append(animation)

    for i in recommend_list:
        try:
            session.add(i)
            session.commit()
        except Exception:
            session.rollback()


def get_bangumi(md_list):
    # # 连接数据库
    # engine = create_engine("mysql+pymysql://root:qw971230@localhost:3306/pilipili")
    # Session = sessionmaker(bind=engine)
    # session = Session()
    print("数据总量：{}".format(len(md_list)))
    for i in md_list:
        try:
            print("——》获取数据")
            html = requests.get(url="https://www.bilibili.com/bangumi/media/md" + str(i))
            selector = etree.HTML(html.text)

            script = selector.xpath("//script")

            data = str(script[4].text).replace("window.__INITIAL_STATE__=", "").replace(
                ";(function(){var s;(s=document.currentScript||document.scripts[document.scripts.length-1]).parentNode.removeChild(s);}());",
                "")

            data = json.loads(data)

            # 番剧名
            name = data["mediaInfo"]["chn_name"]
            # 声优信息
            voice_actors = data["mediaInfo"]["actors"]
            # 职业信息
            staff = data["mediaInfo"]["staff"]
            # 总播放数
            playnum = data["mediaInfo"]["stat"]["views"]
            # 追番人数
            fannum = data["mediaInfo"]["stat"]["favorites"]
            # 弹幕总数
            danmunum = data["mediaInfo"]["stat"]["danmakus"]
            # 评分
            score = data["mediaInfo"]["rating"]["score"]
            # 简介
            info = data["mediaInfo"]["evaluate"]
            # 封面
            logo = data["mediaInfo"]["cover"].replace("http://", "")
            # 开播时间
            start_date = data["mediaInfo"]["publish"]["pub_date"]
            # 更新时间
            update_time = data["mediaInfo"]["episodes"][0]["pub_real_time"]
            num = 0
            episodes = []
            for i in data["mediaInfo"]["episodes"]:
                r = {
                    "logo": i["cover"].replace("http://", ""),
                    "name": i["index_title"],
                    "pub_time": i["pub_real_time"],
                    "ep_id": i["ep_id"],
                    "piece": i["index"]
                }
                episodes.append(r)
                html = requests.get("https://www.bilibili.com/bangumi/play/ep" + str(i["ep_id"]))
                selector = etree.HTML(html.text)
                av_id = selector.xpath(
                    "//div[@id='app']/div[@class='plp-l']/div[@class='media-wrapper']/div[@id='media_module']/div/div/a[@class='av-link']/text()")
                headers = {
                    "Referer": "https://www.bilibili.com/bangumi/play/ep" + str(i["ep_id"]),
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36"
                }
                tmp_html = requests.get(
                    "https://api.bilibili.com/x/v2/reply?callback=jQuery17207202291318839995_1559452053757&"
                    "jsonp=jsonp&pn=1&type=1&oid={}&sort=0&_=1559452055514".format(
                        str(av_id[0]).replace("AV", "")), headers=headers)
                tmp_data = json.loads(
                    str(tmp_html.text).replace("jQuery17207202291318839995_1559452053757(", "").replace(")", ""))
                commentnum = tmp_data["data"]["page"]["acount"]
                r["commentnum"] = commentnum
                num += 1
                # 集数大于30就排除掉
                if num > 30:
                    break
            if num > 30:
                print("数据分集大于30，去除")
                continue
            # 集数
            episodes = {
                "total": num,
                "episodes": episodes
            }
            # 是否完结
            is_end = data["mediaInfo"]["publish"]["is_finish"]
            # 季节
            season = data["mediaInfo"]["param"]["season_type"]

            r = {
                "name": name,
                "voice_actors": voice_actors,
                "staff": staff,
                "playnum": playnum,
                "fannum": fannum,
                "danmunum": danmunum,
                "episodes": episodes,
                "score": score,
                "info": info,
                "logo": logo,
                "start_date": start_date,
                "update_time": update_time,
                "is_end": is_end,
                "season": season
            }

            c = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
            rootdir = os.path.join(c, 'static', 'bangumi', data["mediaInfo"]["chn_name"]).replace("/", "_")
            if not os.path.exists(rootdir):
                os.mkdir(rootdir)

            with open(os.path.join(rootdir, "detail.json"), "w") as f:
                f.write(json.dumps(r))
            print(name + "——》写入成功")
        except Exception:
            print("获取数据出错，继续")


def get_top_bangumi():
    md_list = []
    for i in range(1, 4):
        url = "https://bangumi.bilibili.com/media/web_api/search/result?season_version=-1" \
              "&area=-1&is_finish=-1&copyright=-1&season_status=-1&season_month=-1&pub_date=-1" \
              "&style_id=-1&order=3&st=1&sort=0&page={}&season_type=1&pagesize=20".format(i)
        headers = {
            "Origin": "https://www.bilibili.com",
            "Referer": "https://www.bilibili.com/anime/index",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36"
        }
        html = requests.get(url=url, headers=headers)
        data = json.loads(html.text)
        for j in data["result"]["data"]:
            md_list.append(j["media_id"])
    return md_list


def get_chin_ban():
    md_list = []
    for i in range(1, 3):
        url = "https://bangumi.bilibili.com/media/web_api/search/result?season_version=-1" \
              "&area=-1&is_finish=-1&copyright=-1&season_status=-1&season_month=-1&pub_date=-1" \
              "&style_id=-1&order=5&st=1&sort=0&page={}&season_type=1&pagesize=20".format(i)
        headers = {
            "Origin": "https://www.bilibili.com",
            "Referer": "https://www.bilibili.com/anime/timeline/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36"
        }
        html = requests.get(url=url, headers=headers)
        data = json.loads(html.text)
        for j in data["result"]["data"]:
            md_list.append(j["media_id"])
    return md_list


def get_animation():
    # 连接数据库
    engine = create_engine("mysql+pymysql://qw:qw@971230@134.175.93.183:3306/pilipili")
    Session = sessionmaker(bind=engine)
    session = Session()
    url_list = [
        {"ids": 52, "name": "douga", "tag_id": 1},
        {"ids": 58, "name": "music", "tag_id": 4},
        {"ids": 64, "name": "dance", "tag_id": 5},
        {"ids": 70, "name": "game", "tag_id": 6},
        {"ids": 76, "name": "technology", "tag_id": 7},
        {"ids": 2977, "name": "digital", "tag_id": 8},
        {"ids": 88, "name": "life", "tag_id": 9},
        {"ids": 100, "name": "kichiku", "tag_id": 10},
        {"ids": 94, "name": "fashion", "tag_id": 11},
        {"ids": 82, "name": "ent", "tag_id": 12},
        {"ids": 2211, "name": "cinephile", "tag_id": 13},
        # {"ids": 1634, "name": "放映室","tag_id":},
    ]
    recommend_list = []
    url = "https://api.bilibili.com/x/web-show/res/locs?jsonp=jsonp&ids={}"
    for i in url_list:
        tmp_url = url.format(i["ids"])
        headers = {
            "Referer": "https://www.bilibili.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36"
        }
        result = requests.get(url=tmp_url, headers=headers)
        result = json.loads(result.text)
        data = result["data"][str(i["ids"])]
        for j in data:
            animation = Animation()
            animation.tag_id = i["tag_id"]
            animation.name = j["name"]
            animation.logo = j["pic"]
            animation.url = j["url"] if len(j["url"]) < 500 else None
            recommend_list.append(animation)

    for i in recommend_list:
        session.add(i)
    try:
        session.commit()
    except Exception as e:
        print(e)
        session.rollback()


def LoadUserAgents(uafile):
    uas = []
    with open(uafile, 'rb') as uaf:
        for ua in uaf.readlines():
            if ua:
                uas.append(ua.strip()[:-1])
    random.shuffle(uas)
    return uas


def get_every_top_video():
    """获取每个分类排行版的数据"""
    url_list = ['https://www.bilibili.com/ranking/all/1/0/3', 'https://www.bilibili.com/ranking/all/168/0/3',
                'https://www.bilibili.com/ranking/all/3/0/3', 'https://www.bilibili.com/ranking/all/129/0/3',
                'https://www.bilibili.com/ranking/all/4/0/3', 'https://www.bilibili.com/ranking/all/36/0/3',
                'https://www.bilibili.com/ranking/all/188/0/3', 'https://www.bilibili.com/ranking/all/160/0/3',
                'https://www.bilibili.com/ranking/all/119/0/3', 'https://www.bilibili.com/ranking/all/155/0/3',
                'https://www.bilibili.com/ranking/all/5/0/3', 'https://www.bilibili.com/ranking/all/181/0/3']
    # url_list = ['https://www.bilibili.com/ranking/all/1/0/3']

    av_list = []
    for i in url_list:
        html = requests.get(url=i)
        selector = etree.HTML(html.text)
        content = selector.xpath(
            "//div[@class='rank-body']/div[@class='rank-list-wrap']/ul[@class='rank-list']/li[@class='rank-item']/div[@class='content']/div[@class='info']/a/@href")
        for i in content:
            av_list.append(i.replace("//www.bilibili.com/video/av", "").replace("/", ""))
    uas = LoadUserAgents("user_agents.txt")
    num = 1
    for i in av_list:
        ua = random.choice(uas)
        headers = {
            'User-Agent': ua
        }
        start_url = 'https://api.bilibili.com/x/web-interface/view?aid=' + i
        html = requests.get(start_url, headers=headers).json()
        data = html['data']
        root_dir = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "static", "tmp_video")
        with open(os.path.join(root_dir, str(num) + ".json"), 'w+', encoding='utf-8')as f:
            r = {
                "name": data["title"],
                "info": data["desc"],
                "logo": data["pic"],
                "user": data["owner"]["name"],
                "user_face": data["owner"]["face"],
                "tag": data["tname"],
                "playnum": data["stat"]["view"],
                "danmunum": data["stat"]["danmaku"],
                "commentnum": data["stat"]["reply"],
                "colnum": data["stat"]["favorite"],
                "release_time": data["pubdate"],
            }
            f.write(json.dumps(r, ensure_ascii=False))
        num += 1


def get_bangimi_and_guochang():
    html = requests.get("https://www.bilibili.com/anime")
    selector = etree.HTML(html.text)


def writevideo_2db():
    # 连接数据库
    engine = create_engine("mysql+pymysql://qw:qw@971230@134.175.93.183:3306/pilipili")
    Session = sessionmaker(bind=engine)
    session = Session()
    root_dir = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "static", "tmp_video")
    dir_list = os.listdir(root_dir)
    start = 7000
    for i in range(len(dir_list)):
        with open(os.path.join(root_dir, dir_list[i]), encoding="utf-8") as f:
            data = json.load(f)
            try:
                baseuser = session.query(BaseUser).filter(BaseUser.name == data["user"]).first()
                if not baseuser:
                    baseuser = BaseUser()
                    baseuser.id = start
                    baseuser.name = data["user"]
                    baseuser.gender = GenderEnum.UNKNOWN.value,
                    baseuser.account = start
                    baseuser.pwd = start
                session.add(baseuser)
                session.commit()
            except Exception as e:
                print(e)
                session.rollback()
            # 用户额外信息
            try:
                baseuser = session.query(BaseUser).filter(BaseUser.name == data["user"]).first()
                user = User()
                user.id = baseuser.id
                user.face = data["user_face"]
                session.add(user)
                session.commit()
            except Exception as e:
                print(e)
                session.rollback()
            # 用户角色赋予
            try:
                userrole = UserRole(user_id=baseuser.id, role_id=1)
                session.add(userrole)
                session.commit()
            except Exception as e:
                print(e)
                session.rollback()
            try:
                video = Video()
                video.name = data["name"]
                video.info = data["info"]
                video.logo = data["logo"]
                video.playnum = data["playnum"]
                video.danmunum = data["danmunum"]
                tag = session.query(Tag).filter(Tag.name == data["tag"]).first()
                if tag:
                    video.tag_id = tag.id
                video.commentnum = data["commentnum"]
                video.colnum = data["colnum"]
                video.release_time = datetime.datetime.fromtimestamp(data["release_time"])
                video.user_id = baseuser.id
                session.add(video)
                session.commit()
            except Exception as e:
                print(e)
                session.rollback()

            print(start)
            start += 1


if __name__ == "__main__":
    # get_recommend()
    # md_list = get_top_bangumi()
    # md_list = get_chin_ban()
    # get_bangumi(md_list)
    # get_every_top_video()
    # get_animation()
    get_bangimi_and_guochang()
    # writevideo_2db()
