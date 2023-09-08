import math
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from nonebot.permission import SUPERUSER


__plugin_meta__ = PluginMetadata(
    name='快捷禁言解禁',
    description='快捷禁言解禁',
    usage='禁/解 （时间） @用户',
)


# 禁言
ban = on_command(
    '禁',
    priority=1,
    block=True,
    permission=SUPERUSER
)

# 解禁
unban = on_command(
    '解',
    priority=1,
    block=True,
    permission=SUPERUSER
)


@ban.handle()
async def ban(
        event: GroupMessageEvent,
        bot: Bot,
        args: Message = CommandArg()
) -> str:
    banTime = str(args).strip()
    msg = event.get_message()
    uid = [at.data["qq"] for at in msg["at"]]
    # 处理禁言
    time = 0
    if banTime == '':
        time = 10*60
    elif banTime.isdigit():
        banTime = math.ceil(float(banTime))
        if banTime < 0:
            time = 10 * 60
        else:
            time = banTime
    else:
        ban.finish(MessageSegment.reply(event.message_id) + '请发送正确的禁言时间喵~')

    await bot.set_group_ban(
        user_id=uid[0],
        group_id=event.group_id,
        duration=time * 60
    )
    return f"晚安喵~"


@unban.handle()
async def ban(
        event: GroupMessageEvent,
        bot: Bot,
        args: Message = CommandArg()
) -> str:
    msg = event.get_message()
    uid = [at.data["qq"] for at in msg["at"]]
    # 处理解除禁言
    await bot.set_group_ban(
        user_id=uid[0],
        group_id=event.group_id,
        duration=0
    )
    return f"早安喵~"
