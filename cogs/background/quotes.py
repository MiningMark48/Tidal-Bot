import typing

import aiohttp
import discord
import requests
from bs4 import BeautifulSoup as bs
from discord.ext import commands

from util.messages import MessagesUtil


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.messages_util = MessagesUtil(bot)
        self.quote_emoji = "\N{PUSHPIN}"
        self.webhook_name = "tb-quote"  # TODO: Make config

    @commands.Cog.listener("on_raw_reaction_add")
    async def on_raw_reaction_add(self, payload):
        reaction_emoji = str(payload.emoji)
        user = payload.member
        guild = user.guild
        channel = guild.get_channel(payload.channel_id)
        # msg = await channel.fetch_message(payload.message_id)
        msg = await self.messages_util.get_message(channel, payload.message_id)

        if user == self.bot.user or isinstance(channel, discord.DMChannel): # Bot can't quote itself, and can't be used in DM
            return

        if reaction_emoji == self.quote_emoji:
            webhook = discord.utils.find(lambda w: (isinstance(w, discord.Webhook) and w.name == self.webhook_name), await guild.webhooks())
            if not webhook:  # If webhook doesn't exist, return (do nothing)
                return

            attachments = msg.attachments
            msg_content = msg.content

            if msg_content and not str(msg_content).startswith(">"):
                msg_content = f"> {msg_content}"

            embed = discord.Embed(
                description=f"{msg_content}", color=msg.author.color)
            embed.add_field(name="Jump Link",
                            value=f"[Click Here]({msg.jump_url})")
            embed.set_author(name=msg.author, icon_url=msg.author.avatar_url)
            embed.timestamp = msg.created_at
            embed.set_footer(text=f"Quoted by {user.name}")

            if attachments and attachments[0]:
                embed.set_image(url=attachments[0].url)
            elif not msg_content:
                return

            await webhook.send(embed=embed, username=f"Quote", avatar_url="https://f000.backblazeb2.com/file/miningmark48-files/2020/08/26/quotebot.png")

            await msg.remove_reaction(self.quote_emoji, user)


def setup(bot):
    bot.add_cog(Utility(bot))
