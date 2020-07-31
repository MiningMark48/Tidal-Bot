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
from bs4 import BeautifulSoup as bs
from discord.ext import commands

from util.decorators import delete_original

start_time = time.time()


class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.trans = googletrans.Translator()

    @commands.command(name="placeholderimg", aliases=["placeholder"])
    @delete_original()
    async def placeholder_img(self, ctx, size: str, *, text="Placeholder"):
        """
        Generate a placeholder image

        Usage:
        placeholder 256
        placeholder 512x256 Image
        """

        base_url = "https://via.placeholder.com/{}".format(size)
        payload = {'text': text}
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url, params=payload) as r:
                content = await r.content.read()
                buffer = BytesIO(content)
                f = discord.File(buffer, filename=f'{text}.png')
                await ctx.send(file=f)


def setup(bot):
    bot.add_cog(Images(bot))
