import json
import os.path as osp

from discord.ext import commands


def load_config():
    config_path = "config.json"

    if osp.isfile(config_path):
        with open(config_path, 'r') as file:
            data = json.load(file)
            global bot_owners
            bot_owners = data["bot_owners"]


def is_bot_owner():
    async def predicate(ctx):
        global bot_owners
        if bot_owners and len(bot_owners) > 0:
            return ctx.author.id in bot_owners
        return False
    return commands.check(predicate)


load_config()
