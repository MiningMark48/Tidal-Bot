import json
import os.path as osp

import discord
from discord.ext import commands

import util.gen_list as GenList
import util.userconf as uc
from extensions import EXTENSIONS
from util.data.guild_data import GuildData
from util.help_command import HelpCommand
from util.logger import Logger

from util.data.data_backup import backup_databases

Logger.alert("Starting...")

bot_token = "bot.token"
bot_key = ";"
load_music = True
bot_owners = []
extensions = EXTENSIONS

config_path = "config.json"
resources_path = "./resources/"

def_config = {
    "bot_token": bot_token,
    "bot_key": bot_key,
    "load_music": load_music,
    "bot_owners": bot_owners
}

do_run = True

# global servers_cfg
servers_cfg = None

Logger.info("Loading config...")
if osp.isfile(config_path):
    with open(config_path, 'r') as file:
        data = json.load(file)
        bot_token = data["bot_token"]
        bot_key = data["bot_key"]
        load_music = data["load_music"]
        bot_owners = data["bot_owners"]
        Logger.success("Config loaded.")
else:
    with open(config_path, 'w') as file:
        Logger.warn("Config file not found, creating...")
        json.dump(def_config, file, indent=4)
        Logger.success("Config file created.")
        do_run = False


def prefix(bot, message):
    pfx = bot_key
    if message.guild:
        pfx = GuildData(str(message.guild.id)).strings.fetch_by_name("prefix")
    return pfx if pfx else bot_key


# def_help = commands.DefaultHelpCommand(dm_help=None, dm_help_threshold=750)
bot = commands.Bot(command_prefix=prefix, help_command=HelpCommand())
bot.description = "Tidal Bot is a bot for Discord written by MiningMark48 to serve then needs of The Tidal Waves."


@bot.event
async def on_ready():
    Logger.success(f"We have logged in as {bot.user}")
    await bot.change_presence(activity=discord.Activity(name=f"Do {bot_key}help", type=discord.ActivityType.playing))

    uc.backup_data()
    backup_databases()

    generator = GenList.Generator(bot)
    generator.gen_list()


@bot.event
async def on_message(message):

    if message.author == bot.user:
        return

    ctx = await bot.get_context(message)
    if ctx:
        if ctx.command and ctx.guild:
            if len(GuildData(str(ctx.guild.id)).disabled_commands.fetch_all_by_name(ctx.command.name)) > 0:
                await ctx.send(f'`{ctx.command.name}` has been disabled.')
                return

        # await bot.invoke(ctx) # Uses this so webhooks/bots can use the bot

    await bot.process_commands(message)


# @bot.event
# async def on_guild_remove(guild):
    # TODO: remove server database on guild remove


if __name__ == "__main__":

    if load_music:
        extensions.append("music")

    count = 0
    for extension in extensions:
        try:
            bot.load_extension(f"cogs.{extension}")
            Logger.info(f"[Cog] Loaded {extension}")
            count += 1
        except Exception as error:
            Logger.fatal(f"{extension} cannot be loaded. [{error}]")
    Logger.info(f"Loaded {count}/{len(extensions)} cogs")

if do_run:
    bot.run(bot_token)
else:
    Logger.fatal("Startup aborted.")
