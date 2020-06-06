from nonebot import on_command, CommandSession
from random import randint
from nonebot.log import logger
import logging
import os.path as path
from aiohttp import ClientSession
import nonebot
import cq
import re
import base64
import datetime

doc = {
    "mrfz": "明日方舟",
    "bcr": "公主连接 B服",
    "gcores": "机核网",
    "loli": "忧郁的loli",
    "pprice": "每日生猪价格",
    "bh3": "崩坏3",
    "hpoi": "Hpoi 手办wiki",
    "xl": "b站总运营 乐爷Official",
    "pixiv_day": "Pixiv 每日热榜",
    "pixiv_week": "Pixiv 每周热榜",
    "pixiv_month": "Pixiv 每月热榜",
    "pixiv_week_rookie": "Pixiv 每周新人榜",
    "pixiv_week_original": "Pixiv 每周原创榜",
    "pixiv_day_male": "Pixiv 每日热榜 男性向",
    "pixiv_day_female": "Pixiv 每日热榜 女性向",
    "pixiv_day_r18": "Pixiv 每日热榜 R-18",
    "pixiv_week_r18": "Pixiv 每周热榜 R-18",
    "pixiv_day_male_r18": "Pixiv 每日热榜 男性向 R-18",
    "pixiv_day_female_r18": "Pixiv 每日热榜 女性向 R-18",
    "pixiv_week_r18g": "Pixiv 每周热榜 R18g",
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36",
}


def init():
    file_handler = logging.FileHandler(
        path.join(path.dirname(__file__), "log", "mybot.log")
    )
    file_handler.setLevel(level=logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.info("初始化完毕！准备开始启动服务！")


def isdigit(c: str) -> bool:
    try:
        c = int(c)
    except:
        return False
    return True


def swFormatter(thing: str):
    pre = None
    sw = ""

    for i in range(len(thing)):
        if isdigit(thing[i]):
            sw += thing[i]
        elif thing[i] not in [" ", "-"]:
            sw = ""

    if sw == "" or len(sw) != 12:
        sw = "-1"

    return sw


def hourse(url: str) -> str:
    a = url
    try:
        url = list(url)
        for i in range(5):
            url.insert(randint(0, len(url)), "🐎")
        url = "".join(url)
    except:
        url = "（打🐎失败，请复制到浏览器中打开，不要直接打开！）" + a

    return url


async def sendpic(session: ClientSession, url: str):
    fd = re.search(r"\?", url)
    if fd != None:
        url = url[: fd.span()[0]]
    async with session.get(url) as resp:
        if resp.status != 200:
            pic = None
        else:
            _, pic = path.split(url)
            if path.splitext(pic)[1] == ".gif":
                bot = nonebot.get_bot()
                if not path.exists(bot.config.IMGPATH + pic):
                    with open(bot.config.IMGPATH + pic, "wb") as fl:
                        while True:
                            ck = await resp.content.read(8196)
                            if not ck:
                                break
                            fl.write(ck)
                pic = cq.image(pic)
            else:
                ShitData = await resp.content.read()
                ShitBase64 = base64.b64encode(ShitData)
                pic = cq.image("base64://" + str(ShitBase64, encoding="utf-8"))
    return pic


def transtime(tm: str, fmt: str = "%a, %d %b %Y %H:%M:%S %Z"):
    try:
        tm = datetime.datetime.strptime(tm, fmt)
    except ValueError:
        pass
    return tm
