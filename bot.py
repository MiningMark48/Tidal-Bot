import discord
from discord.ext import commands

import util.gen_list as GenList
from util.extensions import get_extensions
from util.data.data_backup import backup_databases
from util.data.data_delete import delete_database_guild
from util.data.guild_data import GuildData
from util.help_command import HelpCommand
from util.logger import Logger
from util.config import BotConfig

import time

start_time = time.time()

Logger.breakline()
Logger.alert("Starting...")

resources_path = "./resources/"

try:
    Logger.info("Loading config...")
    config = BotConfig()
    config_data = config.data
    bot_data = config_data["bot"]
    bot_token = bot_data["token"]
    bot_key = bot_data["key"]
    bot_owners = bot_data["owners"]
    load_music = config_data["music"]["enabled"]
    create_commands_list = config_data["misc"]["create_commands_list"]

    do_run = config.do_run
except KeyError as e:
    Logger.fatal(f"Config error.\n\tKey Not Loaded: {e}")
    do_run = False

extensions = get_extensions()


def prefix(bot, message):
    pfx = bot_key
    if message.guild:
        data = GuildData(str(message.guild.id)).strings.fetch_by_name("prefix")
        if data:
            pfx = commands.when_mentioned_or(data)(bot, message)
    return pfx if pfx else bot_key


# def_help = commands.DefaultHelpCommand(dm_help=None, dm_help_threshold=750)
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True
intents.reactions = True

bot = commands.Bot(command_prefix=prefix,
                   help_command=HelpCommand(), intents=intents)


@bot.event
async def on_ready():
    Logger.success(f"We have logged in as {bot.user}")
    await bot.change_presence(activity=discord.Activity(
        name=f"Do {bot_key}help", type=discord.ActivityType.playing))

    backup_databases()

    if create_commands_list:
        generator = GenList.Generator(bot)
        generator.gen_md_list()
        # generator.gen_list()
        # generator.gen_img_list()

    Logger.success("Bot started in {} seconds".format(
        str(time.time() - start_time)[:4]))


@bot.event
async def on_message(message):

    if message.author == bot.user:
        return

    ctx = await bot.get_context(message)
    if ctx:
        if ctx.command and ctx.guild:
            if len(GuildData(str(ctx.guild.id)).disabled_commands
                    .fetch_all_by_name(ctx.command.name)) > 0:
                await ctx.send(f'`{ctx.command.name}` has been disabled.')
                return

        # await bot.invoke(ctx) # Uses this so webhooks/bots can use the bot

    if message.webhook_id:
        await bot.invoke(ctx)
    else:
        await bot.process_commands(message)


@bot.event
async def on_guild_join(guild):
    Logger.info(f"Guild | Joined: {guild.id}")


@bot.event
async def on_guild_remove(guild):
    delete_database_guild(str(guild.id))

    Logger.info(f"Guild | Left: {guild.id}")


if __name__ == "__main__":

    if load_music:
        extensions.append("music")

    count = 0
    for extension in extensions:
        try:
            bot.load_extension(f"cogs.{extension}")
            Logger.info(f"Cog | Loaded {extension}")
            count += 1
        except Exception as error:
            Logger.fatal(f"{extension} cannot be loaded. \n\t[{error}]")
    Logger.info(f"Loaded {count}/{len(extensions)} cogs")

if do_run:
    bot.run(str(bot_token))
else:
    Logger.fatal("Startup aborted.")
