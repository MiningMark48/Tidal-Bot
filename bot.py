import json
import os.path as osp
import random
from datetime import datetime, timedelta

import discord
from discord.ext import commands

import util.servconf as sc

print("Starting...")

extensions = ["errors", "fun.fun", "fun.minesweeper", "fun.numberguess", "fun.trivia", "fun.rroulette", "fun.sudoku",
              "fun.xkcd", "images.fakeping", "images.memelicense", "images.memes", "images.progress", "info",
              "moderation.flagging", "owner", "servmng.follow", "servmng.msgjoin", "servmng.prefix", "servmng.toggle",
              "utility.announce", "utility.colorgen", "utility.dictionary", "utility.giveaway", "utility.lyrics",
              "utility.memesearch", "utility.poll", "utility.random", "utility.urbandict", "utility.utility",
              "utility.scale", "utility.wikipedia"]

load_battleship = False
if load_battleship:
    extensions.append("fun.battleship")

bot_token = "bot.token"
bot_key = ";"
load_music = True

config_path = "config.json"
resources_path = "./resources/"

def_config = {
    "bot_token": bot_token,
    "bot_key": bot_key,
    "load_music": load_music
}

do_run = True

global servers_cfg
servers_cfg = None

print("Loading config...")
if osp.isfile(config_path):
    with open(config_path, 'r') as file:
        data = json.load(file)
        bot_token = data["bot_token"]
        bot_key = data["bot_key"]
        load_music = data["load_music"]
        print("Config loaded.")
else:
    with open(config_path, 'w') as file:
        print("Config file not found, creating...")
        json.dump(def_config, file, indent=4)
        print("Config file created.")
        do_run = False


def prefix(bot, message):
    pfx = bot_key
    if message.guild:
        pfx = sc.get_v(str(message.guild.id), "prefix")
    return pfx if pfx else bot_key


def_help = commands.DefaultHelpCommand(dm_help=None, dm_help_threshold=750)
bot = commands.Bot(command_prefix=prefix, help_command=def_help)


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await bot.change_presence(activity=discord.Activity(name=f"Do {bot_key}help", type=discord.ActivityType.playing))


@bot.event
async def on_message(message):
    # start_time = time.time()

    if message.author == bot.user:
        return

    ctx = await bot.get_context(message)
    if ctx:
        if ctx.command and ctx.guild:
            if sc.array_contains(str(ctx.guild.id), ctx.command.name, "command_blacklist"):
                await ctx.send(f'`{ctx.command.name}` has been disabled.')
                return

            now = datetime.now()
            if datetime(now.year, now.month, now.day) == datetime(now.year, 4, 1) and random.randint(0, 25) == 0:
                await ctx.send("Sometimes I feel like people are just using me like I'm a bot or something 🤷")
                return

        # await bot.invoke(ctx) # Uses this so webhooks/bots can use the bot

    await bot.process_commands(message)
    # print(f'{time.time() - start_time} ms') # Delay


@bot.event
async def on_command(ctx):
    if not ctx.guild:
        return

    channel = discord.utils.find(lambda c: (isinstance(c, discord.TextChannel) and "[tb-log]" in (c.topic if c.topic else "")), ctx.guild.channels)
    if channel:
        embed = discord.Embed(title=ctx.command.name, color=ctx.message.author.top_role.color)
        embed.add_field(name="Executed by", value=ctx.author.mention)
        embed.add_field(name="Executed at", value=str(ctx.message.created_at)[:19])
        embed.add_field(name="Message Link", value=f'[Click Here]({ctx.message.jump_url})')
        message_content = ctx.message.content
        embed.add_field(name="Full Message", value=f'{message_content[:100]}...' if len(message_content) > 100 else message_content, inline=False)

        try:
            await channel.send(embed=embed)
        except discord.HTTPException:
            await ctx.send("Error, could not send embed.")


@bot.event
async def on_guild_remove(guild):
    sc.remove_server_data(str(guild.id))

if __name__ == "__main__":

    if load_music:
        extensions.append("music")

    for extension in extensions:
        try:
            bot.load_extension(f"cogs.{extension}")
            print(f"[Cog] Loaded {extension}")
        except Exception as error:
            print(f"{extension} cannot be loaded. [{error}]")

if do_run:
    bot.run(bot_token)
else:
    print("Startup aborted.")
