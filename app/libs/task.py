# coding=UTF-8
"""此模块指定时间完成相应的任务"""
import requests
from lxml import etree
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.log import LoginLog
from app.models.video import Video, Bangumi, Episode

import logging


def calculate_avg_score():
    """计算平均得分"""
    engine = create_engine("mysql+pymysql://root:qw971230@localhost:3306/pilipili")
    Session = sessionmaker(bind=engine)
    session = Session()
    # playnum * 0.5 + colnum * 0.8 + commentnum * 0.7
    for i in session.query(Video).all():
        i.score = i.playnum * 0.5 + i.colnum * 0.8 + i.commentnum * 0.7
        session.add(i)
        session.commit()
    logging.warning("更新平均得分")
    session.close()


def calculate_bangumi():
    """计算番剧总得分、总评论数等等"""
    engine = create_engine("mysql+pymysql://root:qw971230@localhost:3306/pilipili")
    Session = sessionmaker(bind=engine)
    session = Session()
    for i in session.query(Bangumi).all():
        videos = session.query(Video).join(Episode, Episode.video_id == Video.id). \
            filter(i.id == Episode.bangumi_id, Episode.video_id == Video.id)
        for j in videos:
            i.playnum += j.playnum
            i.commentnum += j.commentnum
        session.add(i)
        session.commit()
    logging.warning("更新番剧得分")
    session.close()


def calculate_ip():
    """根据IP计算详细地址"""
    engine = create_engine("mysql+pymysql://root:qw971230@localhost:3306/pilipili")
    Session = sessionmaker(bind=engine)
    session = Session()
    for i in session.query(LoginLog).filter(LoginLog.location == None).all():
        headers = {
            "User-Agent": "PostmanRuntime/7.13.0",
            "Host": "ip.cn",
        }
        html = requests.get("https://ip.cn/index.php?ip=" + i.ip, headers=headers)
        data = etree.HTML(html.text)
        location = data.xpath("//div[@class='container-fluid']/div[@id='result']/div[@class='well']/p[2]/code/text()")
        i.location = location[0] if location else "未知"
    session.close()
