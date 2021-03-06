from nonebot import on_command, CommandSession, on_startup
from nonebot.message import unescape
from datetime import datetime
import nonebot
from aiocqhttp.exceptions import Error as CQHttpError
from nonebot.argparse import ArgumentParser
from nonebot.log import logger
import cq
import requests
import os.path as path
import json
import aiohttp
from bs4 import BeautifulSoup
import re
from utils import headers

url = r"https://search.bilibili.com/all?keyword="

__plugin_name__ = "bili search"


@on_command("bilibili", aliases={"bili", "哔哩哔哩"}, only_to_me=False)
async def bilibili(session: CommandSession):

    keyword = session.get("kw", prompt="请输入你想搜索的内容！")
    if "lmt" in session.state:
        lmt = session.state["lmt"]
    else:
        if session.event.detail_type != "private":
            lmt = 1
        else:
            lmt = 5

    async with aiohttp.ClientSession() as sess:
        async with sess.get(url + keyword, headers=headers) as resp:
            if resp.status != 200:
                session.finish("网络错误：" + str(resp.status))
            ShitHtml = await resp.text()

    sp = BeautifulSoup(ShitHtml, "lxml")

    title = sp.find_all("a", attrs={"class": "title"})

    lmt = min(lmt, len(title))

    if lmt == 0:
        session.finish("未搜索到「{}」的相关内容。".format(keyword))

    if lmt != 1:
        await session.send("以下是「{}」的搜索结果".format(keyword))

    for i in range(lmt):
        res = ""
        res=r'[CQ:json,data={"app":"com.tencent.miniapp_01"&#44;"appID":"100951776"&#44;"bthirdappforward":true&#44;"bthirdappforwardforbackendswitch":true&#44;"config":{"autoSize":0&#44;"ctime":1599824266&#44;"forward":1&#44;"height":0&#44;"token":"e734c12b022b55be28389e6bd3cedf56"&#44;"type":"normal"&#44;"width":0}&#44;"desc":""&#44;"extra":{"app_type":1&#44;"appid":100951776}&#44;"meta":{"detail_1":{"appid":"1109937557"&#44;"desc":" 要来了！AMD首次宣布Zen3处理器/RDNA2显卡"&#44;"host":{"nick":"·"&#44;"uin":545870222}&#44;"icon":"http://i.gtimg.cn/open/app_icon/00/95/17/76//100951776_100_m.png"&#44;"preview":"https://external-30160.picsz.qpic.cn/2a3d18a451c20394e9f9766a9e193971/jpg1"&#44;"qqdocurl":"https://b23.tv/iIpk5A"&#44;"scene":1036&#44;"shareTemplateData":{}&#44;"shareTemplateId":"8C8E89B49BE609866298ADDFF2DBABA4"&#44;"title":"哔哩哔哩"&#44;"url":"m.q.qq.com/a/s/37addc0b7fec2c08419356150b32972d"}}&#44;"prompt":"&#91;QQ小程序&#93;哔哩哔哩"&#44;"ver":"0.0.0.1"&#44;"view":"view_8C8E89B49BE609866298ADDFF2DBABA4"}]'
        if "https" not in title[i].attrs["href"]:
            lk = "https:" + title[i].attrs["href"]
        else:
            lk = title[i].attrs["href"]
        res = ""
        if "bangumi" in title[i].attrs["href"]:
            lk = re.findall(r"^https.*?md[0-9]*", lk)[0]
            num = re.findall(r"media/md[0-9]*", lk)[0]
            num = num[len(r"media/md") :]
            res = "\n该番剧的编号为：" + num
        if "?from=search" in lk:
            lk = lk[: -len("?from=search")]
        if "space" in lk:
            tp = "UP主"
            res += "\n该up主的 uid 为：" + re.findall("[0-9]+", lk)[0]
        elif "biligame" in lk:
            tp = "游戏"
        else:
            tp = "视频标题"
        await session.send("{}：{}\n链接：{}".format(tp, title[i].attrs["title"], lk) + res)

    if lmt > 2:
        session.finish("共返回 {} 条结果。".format(lmt))


@bilibili.args_parser
async def ___(session: CommandSession):
    arg = session.current_arg_text.strip()
    args = arg.split(" ")

    if args[0] == "-m":
        try:
            session.state["lmt"] = int(args[1])
        except:
            session.finish("参数传递错误！")
        arg = " ".join(args[2:])

    if session.is_first_run and arg == "":
        session.pause("请输入你想搜索的内容")

    if arg == "":
        session.pause("输入不能为空哦！")

    session.state["kw"] = arg
