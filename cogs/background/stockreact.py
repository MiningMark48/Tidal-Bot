import re
import asyncio
import discord
from bs4 import BeautifulSoup as bs
from discord.ext import commands


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


        self.pattern = r"\$([A-Za-z]{2,})"
        self.react_emoji = "\N{HEAVY DOLLAR SIGN}"

    @commands.Cog.listener("on_raw_reaction_add")
    async def on_raw_reaction_add(self, payload):
        reaction_emoji = str(payload.emoji)
        user = payload.member
        guild = user.guild
        channel = guild.get_channel(payload.channel_id)
        msg = await channel.fetch_message(payload.message_id)

        if user == self.bot.user or isinstance(channel, discord.DMChannel):
            return

        if reaction_emoji == self.react_emoji:
            alert_msg = await channel.send("Attempting to fetch stock data...")
            msg_content = str(msg.content)

            stock_symbols = re.findall(self.pattern, msg_content)

            for symbol in stock_symbols[:3]:
                ctx = await self.bot.get_context(msg)
                cmd = self.bot.get_command("stock")
                await ctx.invoke(cmd, symbol)

                await asyncio.sleep(1.5)

            await alert_msg.delete()

    @commands.Cog.listener("on_message")
    async def on_message(self, msg):
        if re.findall(self.pattern, msg.content):
            await msg.add_reaction(self.react_emoji)


def setup(bot):
    bot.add_cog(Info(bot))
