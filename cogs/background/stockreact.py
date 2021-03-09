import re
import asyncio
import discord
from bs4 import BeautifulSoup as bs
from discord.ext import commands

from util.data.guild_data import GuildData
from util.messages import MessagesUtil

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.messages_util = MessagesUtil(bot)
        self.pattern = r"\$([A-Za-z]{2,})"
        self.react_emoji = "\N{HEAVY DOLLAR SIGN}"

    @commands.Cog.listener("on_raw_reaction_add")
    async def on_raw_reaction_add(self, payload):
        user = payload.member
        
        if user == self.bot.user:
            return

        reaction_emoji = str(payload.emoji)
        guild = user.guild
        channel = guild.get_channel(payload.channel_id)
        # msg = await channel.fetch_message(payload.message_id)
        msg = await self.messages_util.get_message(channel, payload.message_id)

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

        if not GuildData(str(msg.guild.id)).booleans.fetch_by_name("stock_react"):
            return

        if re.findall(self.pattern, msg.content):
            await msg.add_reaction(self.react_emoji)

    @commands.command(name="togglestockreact", aliases=["togglestock", "stockreact"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    async def toggle_stock_react(self, ctx):
        """Toggle the reaction to messages that may contain stock tickers."""

        result = GuildData(str(ctx.guild.id)).booleans.toggle_boolean("stock_react")
        await ctx.send(f'**{"Enabled" if result else "Disabled"}** the stock reaction.')


def setup(bot):
    bot.add_cog(Info(bot))
