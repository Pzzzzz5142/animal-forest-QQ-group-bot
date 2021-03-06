from nonebot import on_notice, NoticeSession, on_request, RequestSession
from nonebot.message import unescape
import cq


@on_notice("group_increase")
async def hello(session: NoticeSession):
    await session.send(unescape(cq.at(session.event.user_id) + " 欢迎新人入群👏！"))
    await session.bot.send_private_msg(
        user_id=545870222, message=f"新入群 {session.event.group_id}"
    )


@on_request("friend")
async def frd(session: RequestSession):
    # await session.approve()
    await session.send("你好啊，新朋友！")

