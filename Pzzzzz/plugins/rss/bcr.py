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
import feedparser as fp
import re


async def bcr():
    bot = nonebot.get_bot()
    now = datetime.now(pytz.timezone("Asia/Shanghai"))

    thing = fp.parse(r"http://172.18.0.1:1200/bilibili/user/dynamic/353840826")

    async with db.pool.acquire() as conn:
        values = await conn.fetch(f"""select dt from rss where id = 'bcr';""")
        if len(values) == 0:
            await conn.execute(
                f"insert into rss values ('bcr',{thing['entries'][0]['published']})"
            )
        elif thing["entries"][0]["published"] != values[0]["dt"]:
            await conn.execute(
                f"update rss set dt = '{thing['entries'][0]['published']}' where id = 'bcr'"
            )
        else:
            return

    if ("封禁公告" in thing["entries"][0].summary) or (
        "小讲堂" in thing["entries"][0].summary
    ):
        return

    pics = re.findall(
        r"https://.*?\.(?:jpg|jpeg|png|gif|bmp|tiff|ai|cdr|eps)\"",
        thing["entries"][0].summary,
        re.S,
    )

    fdres = re.match(r".*?<br>", thing["entries"][0].summary, re.S)

    text = fdres.string[int(fdres.span()[0]) : fdres.span()[1] - len("<br>")]

    if text[-1] != "\n":
        text += "\n"

    for i in pics:
        text += cq.image(i[:-1])

    try:
        await bot.send_group_msg(group_id=145029700, message=unescape(text))
    except CQHttpError:
        pass
