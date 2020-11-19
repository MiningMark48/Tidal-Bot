import asyncio
import datetime
import html
import re
import string
import time
import typing
from functools import partial
from io import BytesIO
from unicodedata import name

import aiohttp
import discord
import googletrans
from discord.ext import commands

from util.decorators import delete_original

start_time = time.time()


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.trans = googletrans.Translator()

    @commands.command(hidden=True)
    async def binary(self, ctx, method: str, *, message: str):
        """
        [WIP] Encode/Decode to/from binary

        Methods: Encode (e), Decode (d)

        Note: This command is a work-in-progress, some errors may and will occur.
        """

        def binary_to_decimal(binary):
            string = int(binary, 2)
            return string

        if len(message) > 250:
            await ctx.send("Message must be no more than 250 characters.")
            return

        method = method.lower()
        if method in ["encode", "e"]:
            b = ' '.join(format(ord(i), 'b').zfill(8) for i in message)
            await ctx.send(str(b))
        elif method in ["decode", "d"]:
            str_data = ' '
            for i in range(0, len(message), 7):
                temp_data = message[i:i + 7]
                decimal_data = binary_to_decimal(temp_data)
                str_data = str_data + chr(decimal_data)
            await ctx.send(str_data)
        else:
            await ctx.send("INVALID METHOD")

    @commands.command()
    async def countdown(self, ctx, month: int, day: int, year: typing.Optional[int]):
        """
        Get the time remaining to a specific date

        Optional: Year (defaults to current year)
        """

        try:
            today = datetime.date.today()

            if not year:
                year = today.year

            fut_date = datetime.date(year, month, day)
            days = (fut_date - today).days

            fut_date_form = str(fut_date.strftime("%B %e, %Y")).replace("  ", " ")

            await ctx.send(f"There are **{days} days** until **{fut_date_form}**")
        except ValueError:
            await ctx.send("Error! Invalid date!")

    @commands.command(name="createinvite", hidden=True)
    async def create_invite(self, ctx, bot_id: int, perms_int: int):
        """Create a server invite for a bot given perms int and bot id."""

        url = f"https://discord.com/oauth2/authorize?client_id={bot_id}&scope=bot&permissions={perms_int}"
        await ctx.send(f"{ctx.author.mention}, here you go!\n{url}")

    @commands.command(aliases=["emojis"])
    @commands.guild_only()
    async def emojilist(self, ctx):
        """Get a list of all emojis for the server"""
        list = ' '.join(str(x) for x in ctx.guild.emojis)
        await ctx.send(f'**Emojis: **{list}')

    @commands.command(aliases=["gistget"])
    async def gist(self, ctx, code: str):
        """Get the RAW text from a Gist"""
        await ctx.message.delete()

        base_url = f"https://api.github.com/gists/{code}"
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url) as r:
                data = await r.json()
                base_obj = data['files'][next(iter(data['files']))]
                language = base_obj['language']
                content = base_obj['content']

                char_len = 1500
                txt = f'*{code}*\n```{language}\n{(content[:char_len]) if len(content) > char_len else content}``` '

                embed = discord.Embed(title="Gist", color=0xf4cbb2,
                                      url=base_obj["raw_url"])
                embed.description = txt
                embed.set_footer(text="Fetched raw from Gist")

                await ctx.send(embed=embed)

    @commands.command(aliases=["hastebinget", "hasteget", "hb"])
    async def hastebin(self, ctx, code: str):
        """Get the RAW text from a Hastebin"""
        await ctx.message.delete()
        base_url = f"https://hastebin.com/raw/{code}"
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url) as r:
                data = await r.text()
                char_len = 1500
                txt = f'*{code}*\n```{({data[:char_len]}) if len(data) > char_len else data}``` '

                embed = discord.Embed(title="Hastebin", color=0x00222b,
                                      url=base_url)
                embed.description = txt
                embed.set_footer(text="Fetched raw from Hastebin")

                await ctx.send(embed=embed)

    @commands.command(name="matheval", aliases=["evalmath", "calc", "calculator", "math"])
    @commands.cooldown(5, 3)
    async def math_eval(self, ctx, *, expression: str):
        """Evaluate a mathematical expression"""
        try:
            with ctx.typing():
                expression = re.sub(re.compile("([A-Za-z?$#@!{},;:'\"`~|])"), "", expression)
                evaluated = eval(expression)

            embed = discord.Embed(title="Math Evaluation", color=0x4AD473)
            embed.add_field(name="Expression", value=expression, inline=False)
            embed.add_field(name="Result", value=evaluated, inline=False)
            embed.set_footer(text=f"Requested by {ctx.author.display_name}")

            await ctx.send(embed=embed)

        except SyntaxError:
            await ctx.send("Syntax error!")

    @commands.command(aliases=["pastebinget", "pasteget", "pb"])
    async def pastebin(self, ctx, code: str):
        """Get the RAW text from a Pastebin"""
        await ctx.message.delete()
        base_url = f"https://pastebin.com/raw/{code}"
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url) as r:
                data = await r.text()
                char_len = 1500
                txt = f'*{code}*\n```{({data[:char_len]}) if len(data) > char_len else data}``` '

                embed = discord.Embed(title="Pastebin", color=0x023654,
                                      url=base_url)
                embed.description = txt
                embed.set_footer(text="Fetched raw from Pastebin")

                await ctx.send(embed=embed)

    @commands.command()
    @delete_original()
    async def ping(self, ctx):
        """Latency of the bot"""
        await ctx.send(f":ping_pong: Pong! {str(round(self.bot.latency * 1000, 0))[:2]}ms :signal_strength:")

    @commands.command(aliases=["purge", "nuke"])
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def prune(self, ctx, amt: int):
        """Bulk delete messages (up to 100)"""
        if not amt > 0 and amt <= 100:
            await ctx.send(f'Amount must be between **0** and **100**, you entered `{amt}`')
            return
        await ctx.message.delete()
        await ctx.channel.purge(limit=amt)
        msg = await ctx.send(f'Pruned `{amt}` messages.')
        await msg.delete(delay=3)

    @commands.command(aliases=["reminder", "remindme"])
    async def remind(self, ctx, time: int, dm: typing.Optional[bool] = False, *, msg: str):
        """
        Have the bot remind you about something

        Note: Time has a max of 240 minutes (4 hours).
        Also, if the bot goes offline, the reminder is cleared.
        """
        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

        time = max(min(time, 240), 0)
        await ctx.send(f'Ok, I will remind you `{msg}` in **{time}** minutes.', delete_after=10)

        await asyncio.sleep(time * 60)

        text = f'{ctx.author.mention}, this is your reminder: `{msg}`.'
        if not dm:
            await ctx.send(text)
        else:
            await ctx.author.send(text)

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def say(self, ctx, *, msg: str):
        """Make the bot say something"""
        await ctx.message.delete()
        await ctx.send(msg)

    @commands.command(hidden=True)
    @delete_original()
    async def tally(self, ctx, tally_amt: int, *, tally_name: str):
        """Create a simple tally"""

        tally_amt = max(0, min(20, tally_amt))

        embed = discord.Embed(title=f"Tally: {tally_name}")
        embed.description = "Click on the reactions below to tally."

        tallies = [to_emoji(e) for e in range(0, tally_amt)]

        msg = await ctx.send(embed=embed)

        for tally in tallies:
            await msg.add_reaction(tally)

    # noinspection PyBroadException
    @commands.command()
    @delete_original()
    async def translate(self, ctx, language: str, *, msg: str):
        """Translate from a detected language to a specified language"""

        loop = self.bot.loop

        try:
            fn = partial(self.trans.translate, dest=language)
            ret = await loop.run_in_executor(None, fn, msg)
        except Exception as e:
            return await ctx.send(f'An error occurred: `{e.__class__.__name__}: {e}`')

        embed = discord.Embed(title='Translate', colour=0xD8502F)
        src = googletrans.LANGUAGES.get(ret.src, '(auto-detected)').title()
        dest = googletrans.LANGUAGES.get(ret.dest, 'Unknown').title()
        embed.add_field(name=f'From {src}', value=ret.origin, inline=False)
        embed.add_field(name=f'To {dest}', value=ret.text, inline=False)

        await ctx.send(embed=embed)

    @commands.command(aliases=["emojieval", "evalemoji", "evalunicode", "uce"])
    @commands.guild_only()
    async def unicodeeval(self, ctx, char: str):
        """[WIP] Evalutate a Unicode character or an emoji"""
        if len(char) == 1:
            hex = 'U+{:X}'.format(ord(char))
            await ctx.send(f'**Unicode Evaluation:**\n`{hex}` `{char}` {char} *{name(char)}*')
        else:
            await ctx.send("Unicode must be a single character.")

    @commands.command()
    async def uptime(self, ctx):
        """See how long the bot has been running"""
        current_time = time.time()
        difference = int(round(current_time - start_time))
        time_d = datetime.timedelta(seconds=difference)

        days = time_d.days
        hours = time_d.seconds // 3600
        minutes = (time_d.seconds // 60) % 60
        seconds = time_d.seconds % 60

        text_days = f'{days} day{"" if days == 1 else "s"}'
        text_hours = f'{hours} hour{"" if hours == 1 else "s"}'
        text_minutes = f'{minutes} minute{"" if minutes == 1 else "s"}'
        text_seconds = f'{seconds} second{"" if seconds == 1 else "s"}'
        text = f'{text_days}, {text_hours}, {text_minutes}, and {text_seconds}'

        embed = discord.Embed(title="Uptime", color=ctx.message.author.top_role.color)
        embed.description = text
        try:
            await ctx.send(embed=embed)
        except discord.HTTPException:
            await ctx.send("Current uptime: " + text)

    @commands.command(name="urlshorten", aliases=["tinyurl"])
    async def url_shortnen(self, ctx, url: str):
        """Shorten a URL"""

        base_url = "https://tinyurl.com/api-create.php?url={}"

        async with aiohttp.ClientSession() as session:
            async with session.get(base_url.format(url)) as r:
                content = await r.text()
                shortened = str(content)

                embed = discord.Embed(title="Shortened URL", color=0x081f38)
                embed.add_field(name="Original", value=url, inline=False)
                embed.add_field(name="Shortened", value=shortened, inline=False)
                embed.set_footer(text="Shortened with TinyURL")
                await ctx.send(embed=embed)

    @commands.command(name="whatday", aliases=["dayoftheweek", "dotw"])
    async def what_day(self, ctx, month: int, day: int, year: typing.Optional[int]):
        """
        Find out what day of the week a date falls on

        Optional: Year (defaults to current year)
        """

        try:
            today = datetime.date.today()

            if not year:
                year = today.year

            fut_date = datetime.date(year, month, day)
            dotw = fut_date.strftime('%A')

            fut_date_form = str(fut_date.strftime("%B %e, %Y")).replace("  ", " ")

            await ctx.send(f"**{fut_date_form}** is a **{dotw}**.")
        except ValueError:
            await ctx.send("Error! Invalid date!")

    @commands.command(name="youtubestatus", aliases=["ytstatus"], hidden=True)
    async def youtube_status(self, ctx, user: discord.Member):
        """
        Get the YouTube URL from someone's custom status.

        Ex: John#0001 has the status `dQw4w9WgXcQ`. The command will return https://www.youtube.com/watch?v=dQw4w9WgXcQ.
        """

        base_url = "https://www.youtube.com/watch?v="
        activity = str(user.activity)
        activity = re.sub(r"<.+>", "", activity)
        activity = activity.replace(" ", "")
        await ctx.send(f"{base_url}{activity}")


def to_emoji(c):
    base = 0x1f1e6
    return chr(base + c)


def setup(bot):
    bot.add_cog(Utility(bot))
