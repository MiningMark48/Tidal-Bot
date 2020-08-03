import json
import os.path as osp

from discord.ext import commands

from util.config import BotConfig

def load_config():
    data = BotConfig().load_data()
    global bot_owners
    bot_owners = data["bot"]["owners"]


def is_bot_owner():
    async def predicate(ctx):
        global bot_owners
        if bot_owners and len(bot_owners) > 0:
            return ctx.author.id in bot_owners
        return False
    return commands.check(predicate)


load_config()
