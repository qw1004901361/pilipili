# !/usr/bin/python
# -*- coding:utf-8 -*-
# time: 2019/04/17--08:12
import copy
import random

from lxml import etree

__author__ = 'Henry'

'''
项目: B站视频下载

版本1: 加密API版,不需要加入cookie,直接即可下载1080p视频

20190422 - 增加多P视频单独下载其中一集的功能
'''
import imageio

# imageio.plugins.ffmpeg.download()

import requests, time, hashlib, urllib.request, re, json
from moviepy.editor import *
import os, sys


def LoadUserAgents(uafile):
    uas = []
    with open(uafile, 'rb') as uaf:
        for ua in uaf.readlines():
            if ua:
                uas.append(ua.strip()[:-1])
    random.shuffle(uas)
    return uas


# 访问API地址
def get_play_list(start_url, cid, quality):
    entropy = 'rbMCKn@KuamXWlPMoJGsKcbiJKUfkPF_8dABscJntvqhRSETg'
    appkey, sec = ''.join([chr(ord(i) + 2) for i in entropy[::-1]]).split(':')
    params = 'appkey=%s&cid=%s&otype=json&qn=%s&quality=%s&type=' % (appkey, cid, quality, quality)
    chksum = hashlib.md5(bytes(params + sec, 'utf8')).hexdigest()
    url_api = 'https://interface.bilibili.com/v2/playurl?%s&sign=%s' % (params, chksum)
    headers = {
        'Referer': start_url,  # 注意加上referer
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
    }
    # print(url_api)
    html = requests.get(url_api, headers=headers).json()
    # print(json.dumps(html))
    video_list = [html['durl'][0]['url']]
    # print(video_list)
    return video_list


# 下载视频
'''
 urllib.urlretrieve 的回调函数：
def callbackfunc(blocknum, blocksize, totalsize):
    @blocknum:  已经下载的数据块
    @blocksize: 数据块的大小
    @totalsize: 远程文件的大小
'''


def Schedule_cmd(blocknum, blocksize, totalsize):
    speed = (blocknum * blocksize) / (time.time() - start_time)
    # speed_str = " Speed: %.2f" % speed
    speed_str = " Speed: %s" % format_size(speed)
    recv_size = blocknum * blocksize

    # 设置下载进度条
    f = sys.stdout
    pervent = recv_size / totalsize
    percent_str = "%.2f%%" % (pervent * 100)
    n = round(pervent * 50)
    s = ('#' * n).ljust(50, '-')
    f.write(percent_str.ljust(8, ' ') + '[' + s + ']' + speed_str)
    f.flush()
    # time.sleep(0.1)
    f.write('\r')


def Schedule(blocknum, blocksize, totalsize):
    speed = (blocknum * blocksize) / (time.time() - start_time)
    # speed_str = " Speed: %.2f" % speed
    speed_str = " Speed: %s" % format_size(speed)
    recv_size = blocknum * blocksize

    # 设置下载进度条
    f = sys.stdout
    pervent = recv_size / totalsize
    percent_str = "%.2f%%" % (pervent * 100)
    n = round(pervent * 50)
    s = ('#' * n).ljust(50, '-')
    print(percent_str.ljust(6, ' ') + '-' + speed_str)
    f.flush()
    time.sleep(2)
    # print('\r')


# 字节bytes转化K\M\G
def format_size(bytes):
    try:
        bytes = float(bytes)
        kb = bytes / 1024
    except:
        print("传入的字节格式不对")
        return "Error"
    if kb >= 1024:
        M = kb / 1024
        if M >= 1024:
            G = M / 1024
            return "%.3fG" % (G)
        else:
            return "%.3fM" % (M)
    else:
        return "%.3fK" % (kb)


#  下载视频
def down_video(video_list, title, start_url, page, data):
    num = 1
    print('[正在下载P{}段视频,请稍等...]:'.format(page) + title)

    a = os.path.dirname(__file__)
    b = os.path.dirname(a)
    c = os.path.abspath(b)
    currentVideoPath = os.path.join(c, 'static', 'bilibili_video', title)  # 下载目录

    for i in video_list:
        opener = urllib.request.build_opener()
        # 请求头
        opener.addheaders = [
            # ('Host', 'upos-hz-mirrorks3.acgvideo.com'),  #注意修改host,不用也行
            ('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:56.0) Gecko/20100101 Firefox/56.0'),
            ('Accept', '*/*'),
            ('Accept-Language', 'en-US,en;q=0.5'),
            ('Accept-Encoding', 'gzip, deflate, br'),
            ('Range', 'bytes=0-'),  # Range 的值要为 bytes=0- 才能下载完整视频
            ('Referer', start_url),  # 注意修改referer,必须要加的!
            ('Origin', 'https://www.bilibili.com'),
            ('Connection', 'keep-alive'),
        ]
        urllib.request.install_opener(opener)
        # 创建文件夹存放下载的视频
        if not os.path.exists(currentVideoPath):
            os.makedirs(currentVideoPath)

        # 写入json数据
        write_data(currentVideoPath, data)

        # 开始下载
        if len(video_list) > 1:
            urllib.request.urlretrieve(url=i, filename=os.path.join(currentVideoPath, r'{}-{}.flv'.format(title, num)),
                                       reporthook=Schedule_cmd)  # 写成mp4也行  title + '-' + num + '.flv'
        else:
            urllib.request.urlretrieve(url=i, filename=os.path.join(currentVideoPath, r'{}.flv'.format(title)),
                                       reporthook=Schedule_cmd)  # 写成mp4也行  title + '-' + num + '.flv'
        num += 1


# 合并视频
def combine_video(video_list, title):
    currentVideoPath = os.path.join(sys.path[0], 'bilibili_video', title)  # 当前目录作为下载目录
    if len(video_list) >= 2:
        # 视频大于一段才要合并
        print('[下载完成,正在合并视频...]:' + title)
        # 定义一个数组
        L = []
        # 访问 video 文件夹 (假设视频都放在这里面)
        root_dir = currentVideoPath
        # 遍历所有文件
        for file in sorted(os.listdir(root_dir), key=lambda x: int(x[x.rindex("-") + 1:x.rindex(".")])):
            # 如果后缀名为 .mp4/.flv
            if os.path.splitext(file)[1] == '.flv':
                # 拼接成完整路径
                filePath = os.path.join(root_dir, file)
                # 载入视频
                video = VideoFileClip(filePath)
                # 添加到数组
                L.append(video)
        # 拼接视频
        final_clip = concatenate_videoclips(L)
        # 生成目标视频文件
        final_clip.to_videofile(os.path.join(root_dir, r'{}.mp4'.format(title)), fps=24, remove_temp=False)
        print('[视频合并完成]' + title)

    else:
        # 视频只有一段则直接打印下载完成
        print('[视频合并完成]:' + title)


def write_data(path, data):
    with open(path + "\\detail.json", 'w+', encoding='utf-8')as f:
        r = {
            "name": data["title"],
            "info": data["desc"],
            "logo": data["pic"],
            "user": data["owner"]["name"],
            "user_face": data["owner"]["face"],
            "tag": data["tname"],
            "playnum": data["stat"]["view"],
            "commentnum": data["stat"]["reply"],
            "colnum": data["stat"]["favorite"],
            "release_time": data["pubdate"],
        }

        f.write(json.dumps(r))


# 分P视频下载测试: https://www.bilibili.com/video/av19516333/

def start_download(av_list):
    uas = LoadUserAgents("user_agents.txt")
    num = 1
    new_list = copy.deepcopy(av_list)
    for i in av_list:
        start = i
        if start.isdigit() == True:  # 如果输入的是av号
            # 获取cid的api, 传入aid即可
            start_url = 'https://api.bilibili.com/x/web-interface/view?aid=' + start
        else:
            # https://www.bilibili.com/video/av46958874/?spm_id_from=333.334.b_63686965665f7265636f6d6d656e64.16
            start_url = 'https://api.bilibili.com/x/web-interface/view?aid=' + re.search(r'/av(\d+)/*', start).group(1)

        # 视频质量
        # <accept_format><![CDATA[flv,flv720,flv480,flv360]]></accept_format>
        # <accept_description><![CDATA[高清 1080P,高清 720P,清晰 480P,流畅 360P]]></accept_description>
        # <accept_quality><![CDATA[80,64,32,16]]></accept_quality>
        # quality = input('请输入您要下载视频的清晰度(1080p:80;720p:64;480p:32;360p:16)(填写80或64或32或16):')
        quality = 80
        # 获取视频的cid,title

        ua = random.choice(uas)

        headers = {
            'User-Agent': ua
        }
        html = requests.get(start_url, headers=headers).json()
        data = html['data']
        video_title = data["title"].replace(" ", "_")
        cid_list = []
        if '?p=' in start:
            # 单独下载分P视频中的一集
            p = re.search(r'\?p=(\d+)', start).group(1)
            cid_list.append(data['pages'][int(p) - 1])
        else:
            # 如果p不存在就是全集下载
            cid_list = data['pages']

        a = os.path.dirname(__file__)
        b = os.path.dirname(a)
        c = os.path.abspath(b)
        rootdir = os.path.join(c, 'static', 'bilibili_video')
        dir_list = os.listdir(rootdir)

        # print(cid_list)
        for item in cid_list:
            cid = str(item['cid'])
            title = item['part']
            if not title:
                title = video_title
            # title = video_title
            title = re.sub(r'[\/\\:*?"<>|]', '', title)  # 替换为空的
            print("下载第{}个视频".format(num))
            print('[下载视频的cid]:' + cid)
            print('[下载视频的标题]:' + title)
            page = str(item['page'])
            start_url = start_url + "/?p=" + page
            video_list = get_play_list(start_url, cid, quality)
            global start_time
            start_time = time.time()
            num += 1
            if title in dir_list:
                # 如果文件夹下已有，跳过
                sub_dir = os.path.join(rootdir, title)
                if os.path.isfile(os.path.join(sub_dir, title + ".flv")):
                    # 删除
                    new_list.remove(i)
                    write_av_list("av_list.txt", new_list)
                    print('已存在，继续下载')
                    print("")
                    continue

            down_video(video_list, title, start_url, page, data)

            combine_video(video_list, title)

            time.sleep(5)

            # 删除
            new_list.remove(i)
            write_av_list("av_list.txt", new_list)
            print("")

    # 如果是windows系统，下载完成后打开下载目录
    a = os.path.dirname(__file__)
    b = os.path.dirname(a)
    c = os.path.abspath(b)
    currentVideoPath = os.path.join(c, 'static', 'bilibili_video')  # 当前目录作为下载目录
    if (sys.platform.startswith('win')):
        os.startfile(currentVideoPath)


def get_every_top():
    # url_list = ['https://www.bilibili.com/ranking/all/1/0/3', 'https://www.bilibili.com/ranking/all/168/0/3',
    #             'https://www.bilibili.com/ranking/all/3/0/3', 'https://www.bilibili.com/ranking/all/129/0/3',
    #             'https://www.bilibili.com/ranking/all/4/0/3', 'https://www.bilibili.com/ranking/all/36/0/3',
    #             'https://www.bilibili.com/ranking/all/188/0/3', 'https://www.bilibili.com/ranking/all/160/0/3',
    #             'https://www.bilibili.com/ranking/all/119/0/3', 'https://www.bilibili.com/ranking/all/155/0/3',
    #             'https://www.bilibili.com/ranking/all/5/0/3', 'https://www.bilibili.com/ranking/all/181/0/3']

    url_list = ['https://www.bilibili.com/ranking/all/1/0/3']
    av_list = []
    for i in url_list:
        html = requests.get(url=i)
        selector = etree.HTML(html.text)
        content = selector.xpath(
            "//div[@class='rank-body']/div[@class='rank-list-wrap']/ul[@class='rank-list']/li[@class='rank-item']/div[@class='content']/div[@class='info']/a/@href")
        # num = 0
        for i in content:
            av_list.append(i.replace("//www.bilibili.com/video/av", "").replace("/", ""))
            # num += 1
            # if num == 100:
            #     break
    return av_list


def load_av_list(path):
    av_list = []
    with open(path) as f:
        for i in f.readlines():
            av_list.append(i.replace("\n", ""))
    return av_list


def write_av_list(path, data):
    with open(path, "w") as f:
        for i in data:
            f.write(i + "\n")


if __name__ == '__main__':
    av_list = ["54119083"]
    # write_av_list("av_list.txt", av_list)
    # print(av_list)
    # av_list = load_av_list("av_list.txt")
    # print(av_list)
    start_download(av_list)
