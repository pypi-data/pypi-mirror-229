from .adventurer import Adventurer
from .dndcards import dnd_cache_cards, dnd_cards, dnd_rolls

from dicergirl.utils.utils import format_msg, get_status, get_mentions, is_super_user, on_startswith
from dicergirl.utils.parser import CommandParser, Commands, Only, Optional, Required

from nonebot.matcher import Matcher
from nonebot.adapters import Bot as Bot
from nonebot.adapters.onebot.v11 import Bot as V11Bot
from nonebot.internal.matcher.matcher import Matcher
from nonebot.adapters.onebot.v11 import GroupMessageEvent

dndcommand = on_startswith(".dnd", priority=1, block=True).handle()

async def dnd_handler(matcher: Matcher, event: GroupMessageEvent):
    """ DND 车卡指令 """
    args = format_msg(event.get_message(), begin=".dnd", zh_en=True)
    qid = event.get_user_id()
    commands = CommandParser(
        Commands([
            Only("cache", False),
            Optional("set", int),
            Optional("age", int, 20),
            Optional("name", str),
            Optional("sex", str, "女"),
            Optional("roll", int, 1)
            ]),
        args=args,
        auto=True
        ).results
    toroll = commands["roll"]

    if commands["set"]:
        dnd_cards.update(event, dnd_rolls[qid][commands["set"]], save=True)
        inv = Adventurer().load(dnd_rolls[qid][commands["set"]])
        await matcher.send(f"使用序列 {commands['set']} 卡:\n{inv.output()}")
        dnd_rolls[qid] = {}
        return

    age = commands["age"]
    name = commands["name"]

    if not (15 <= age and age < 90):
        await matcher.send(Adventurer().age_change(age))
        return

    reply = ""
    if qid in dnd_rolls.keys():
        rolled = len(dnd_rolls[qid].keys())
    else:
        dnd_rolls[qid] = {}
        rolled = 0

    for i in range(toroll):
        inv = Adventurer()
        inv.age_change(age)
        inv.sex = commands["sex"]

        if name:
            inv.name = name

        dnd_rolls[qid][rolled+i] = inv.__dict__
        count = inv.rollcount()
        reply += f"天命编号: {rolled+i}\n"
        reply += inv.output() + "\n"
        reply += f"共计: {count[0]}/{count[1]}\n"

    if toroll == 1:
        dnd_cache_cards.update(event, inv.__dict__, save=False)

    reply.rstrip("\n")
    await matcher.send(reply)

commands = {"dndcommand": "dnd_handler"}