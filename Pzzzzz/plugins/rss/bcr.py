from nonebot import on_command, CommandSession, on_startup
from nonebot.message import unescape
import asyncio
import asyncpg
from datetime import datetime
import nonebot
import pytz
from aiocqhttp.exceptions import Error as CQHttpError
import yaml
import os
from nonebot.argparse import ArgumentParser
import sys
from nonebot.log import logger
from random import randint
import random
import bisect
from db import db
import cq
from utils import *
from .utils import sendrss
import feedparser as fp
import re


async def bcr():
    bot = nonebot.get_bot()
    now = datetime.now(pytz.timezone("Asia/Shanghai"))

    async with db.pool.acquire() as conn:
        values = await conn.fetch(f"""select dt from rss where id = 'bcr';""")
        if len(values) == 0:
            raise Exception

        ress = await getbcr()

        _, dt = ress[0]
        if dt != values[0]["dt"]:
            await conn.execute(f"update rss set dt = '{dt}' where id = 'bcr'")
            try:
                await bot.send_group_msg(
                    group_id=145029700,
                    message=f"「{doc['bcr']}」有新公告啦！输入 rss bcr 即可查看！已订阅用户请检查私信。",
                )
            except CQHttpError:
                pass

        values = await conn.fetch(f"""select qid, dt from subs where rss = 'bcr'; """)

        for item in values:
            if item["dt"] != dt:
                await sendrss(item["qid"], bot, "bcr", ress)


async def getbcr(max_num: int = -1):
    thing = fp.parse(r"http://172.18.0.1:1200/bilibili/user/dynamic/353840826")

    ress = [(["暂时没有有用的新公告哦！"], thing["entries"][0]["published"])]

    cnt = 0
    is_viewed = False

    for item in thing["entries"]:

        if max_num != -1 and cnt >= max_num:
            break

        if ("封禁公告" in item.summary) or ("小讲堂" in item.summary):
            continue

        fdres = re.match(r".*?<br>", item.summary, re.S)

        text = fdres.string[int(fdres.span()[0]) : fdres.span()[1] - len("<br>")]

        while len(text) > 1 and text[-1] == "\n":
            text = text[:-1]

        pics = re.findall(
            r"https://(?:(?!https://).)*?\.(?:jpg|jpeg|png|gif|bmp|tiff|ai|cdr|eps)\"",
            item.summary,
            re.S,
        )
        text = [text]

        for i in pics:
            text.append(cq.image(i[:-1]))
        ress.append((text, item["published"]))

        cnt += 1

    if len(ress) >= 1:
        ress = ress[1:]

    return ress


async def sendbcr(qid, bot, res=None, dt=None):
    if res == None or dt == None:
        res, dt = await getbcr()

    flg = 1

    async with db.pool.acquire() as conn:
        try:
            await bot.send_private_msg(user_id=qid, message=res)
            await conn.execute(
                f"""update subs set dt = '{dt}' where qid = {qid} and rss = 'bcr';"""
            )
        except CQHttpError:
            flg = 0
            await bot.send_group_msg(
                group_id=145029700,
                message=unescape(cq.at(qid) + "貌似公告并没有发送成功，请尝试与我创建临时会话。"),
            )

    return flg
