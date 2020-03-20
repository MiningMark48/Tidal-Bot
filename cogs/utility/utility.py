import asyncio
import datetime
import random
import time
import typing
from datetime import datetime as dt
from io import BytesIO
from time import gmtime, strftime
from unicodedata import name

import discord
import requests
from discord.ext import commands

start_time = time.time()


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["emojieval", "evalemoji", "evalunicode", "uce"])
    @commands.guild_only()
    async def unicodeeval(self, ctx, char: str):
        """[WIP] Evalutate a Unicode character or an emoji"""
        if len(char) == 1:
            hex = 'U+{:X}'.format(ord(char))
            await ctx.send(f'**Unicode Evaluation:**\n`{hex}` [`N/A`] `{char}` {char} *{name(char)}*')
        else:
            await ctx.send("Unicode must be a single character.")

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
        url = requests.get(base_url, timeout=0.5)
        data = url.json()
        base_obj = data['files'][next(iter(data['files']))]
        language = base_obj['language']
        content = base_obj['content']

        txt = f'**Gist** (*{code}*): ```{language}\n{(content[:1500]) if len(content) > 1500 else content}``` ' \
              f'Visit {base_obj["raw_url"]} for more'

        await ctx.send(txt)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def giveaway(self, ctx, time: int, *, giveaway: str):
        """
        Create a giveaway for users to join.

        Usage: giveaway <time (minutes)> <Giveaway Name>
        Ex: giveaway 60 Free Hugs

        Note: Time must be between 1 minute and 60 minutes.
        """

        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

        reaction_emoji = "🎉"

        if 0 < time <= 60:
            end_time = dt.now() + datetime.timedelta(minutes=time)
            # timezone = "".join(c[0] for c in strftime("%Z", gmtime()).split())
            timezone = strftime("%Z", gmtime())

            embed = discord.Embed(title=f"{reaction_emoji} Giveaway {reaction_emoji}", color=0xfc68a6)
            embed.description = f'**{giveaway}**\n\n' \
                                f'React with {reaction_emoji} to enter!\n\n' \
                                f'Ends at: \n{end_time.strftime("%I:%M:%S %p")}\n*{timezone}*'
            embed.set_footer(text=f'Created by {ctx.author.display_name}')

            msg = await ctx.send(embed=embed)
            await msg.add_reaction(reaction_emoji)

            await asyncio.sleep(time*60)

            entries = []

            r_msg = await ctx.channel.fetch_message(msg.id)

            for reac in r_msg.reactions:
                if reac.emoji == reaction_emoji:
                    async for usr in reac.users():
                        if not usr.bot:
                            entries.append(usr)

            await r_msg.clear_reactions()

            if entries:
                embed.description = f"**{giveaway}**\n\n" \
                                    f"Giveaway Over!\n\n" \
                                    f"Drawing winner..."
                await r_msg.edit(embed=embed)
                await asyncio.sleep(1)

                winning_entry = random.choice(entries)
                embed.description = f"**{giveaway}**\n\n" \
                                    f"Giveaway Over!\n\n" \
                                    f"Out of {len(entries)} entr{'y' if len(entries) == 1 else 'ies'},\n" \
                                    f"{winning_entry.mention} is the winner!"
                await r_msg.edit(embed=embed)

                await ctx.author.send(f'Your giveaway `{giveaway}` just ended in {ctx.guild.name}. '
                                      f'{winning_entry.mention} was the winner.')
                await winning_entry.send(f'{winning_entry.mention}, you won the giveaway `{giveaway}` '
                                         f'in {ctx.guild.name}!')

            else:
                embed.description = f"Giveaway Over!\n\n" \
                                    f"Nobody entered the giveaway."
                await r_msg.edit(embed=embed)

                await ctx.author.send(f'Your giveaway `{giveaway}` just ended in {ctx.guild.name}. '
                                      f'There were no entries, so nobody won.')

    @commands.command(aliases=["pastebinget", "pasteget", "pb"])
    async def pastebin(self, ctx, code: str):
        """Get the RAW text from a Pastebin"""
        await ctx.message.delete()
        base_url = f"https://pastebin.com/raw/{code}"
        url = requests.get(base_url, timeout=0.5)
        data = url.text
        txt = f'**Pastebin** (*{code}*): ```{({data[:1500]}) if len(data) > 1500 else data}``` ' \
              f'Visit {base_url} for more'
        await ctx.send(txt)

    @commands.command(name="pidigit", aliases=['piindex'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pi_digit(self, ctx, num: int):
        """Search for Digits in Pi (up to a million digits)"""
        with open('resources/pi_million_digits.txt', 'r') as file:
            digits = file.read().replace('\n', '')[2:]
            try:
                index = digits.index(str(num))
                await ctx.send(f'Found `{num}` at the index of `{index}`')
            except ValueError:
                await ctx.send(f'Unable to find `{num}` within a million digits of Pi.')

    @commands.command()
    async def ping(self, ctx):
        """Latency of the bot"""
        await ctx.send(f":ping_pong: Pong! {str(round(self.bot.latency * 1000, 0))[:2]}ms :signal_strength:")
        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.message.delete()

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

    @commands.command(aliases=["qrcodecreate", "createqr", "qr"])
    async def qrcode(self, ctx, *, text: str):
        """Generate a QR Code from a string of text"""
        base_url = f"http://api.qrserver.com/v1/create-qr-code/"
        payload = {'size': '200x200', 'margin': '10', 'bgcolor': 'ffffff', 'color': '000000', 'data': text}
        r = requests.get(base_url, params=payload, timeout=0.5)
        buffer = BytesIO(r.content)
        f = discord.File(buffer, filename=f'{text}.png')
        await ctx.send(file=f)

    @commands.command(aliases=["botstats"])
    async def stats(self, ctx):
        """Stats about the bot"""
        embed = discord.Embed(title="Bot Stats", color=ctx.message.author.top_role.color)
        embed.add_field(name="Latency", value=f"{str(round(self.bot.latency * 1000, 0))[:2]}ms")
        embed.add_field(name="Connected Servers", value=len(self.bot.guilds))
        embed.add_field(name="Users", value=len(self.bot.users))
        try:
            await ctx.send(embed=embed)
        except discord.HTTPException:
            await ctx.send("Error sending embeded message, please try again later")

    @commands.command()
    async def uptime(self, ctx):
        """See how long the bot has been running"""
        current_time = time.time()
        difference = int(round(current_time - start_time))
        time_d = datetime.timedelta(seconds=difference)
        
        days = time_d.days
        hours = time_d.seconds//3600
        minutes = (time_d.seconds//60)%60
        seconds = time_d.seconds%60

        text_days = f'{days} day{"" if days == 1 else "s"}'
        text_hours = f'{hours} hour{"" if hours == 1 else "s"}'
        text_minutes = f'{minutes} minute{"" if minutes == 1 else "s"}'
        text_seconds = f'{seconds} second{"" if seconds == 1 else "s"}'
        text = f'{text_days}, {text_hours}, {text_minutes}, and {text_seconds}'

        embed = discord.Embed(title="Uptime", color=ctx.message.author.top_role.color)
        embed.add_field(name="--", value=text)
        try:
            await ctx.send(embed=embed)
        except discord.HTTPException:
            await ctx.send("Current uptime: " + text)

    @commands.command(aliases=["reminder", "remindme"])
    @commands.has_permissions()
    async def remind(self, ctx, time: int, dm: typing.Optional[bool]=False, *, msg: str):
        """
        Have the bot remind you about something

        Note: Time has a max of 120 minutes (2 hours).
        Also, if the bot goes offline, the reminder is cleared.
        """
        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

        time = max(min(time, 120), 0)
        await ctx.send(f'Ok, I will remind you `{msg}` in **{time}** minutes.', delete_after=10)

        await asyncio.sleep(time*60)

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


def setup(bot):
    bot.add_cog(Utility(bot))
