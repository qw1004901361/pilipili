# coding=UTF-8
import json
import os
import re

import requests
from lxml import etree
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.video import Animation


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
        animation.logo = j.replace("https://", "").replace("//", "")
        animation.url = i.replace("https://", "")
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


if __name__ == "__main__":
    # get_recommend()
    # md_list = get_top_bangumi()
    md_list = get_chin_ban()
    get_bangumi(md_list)
