import random

import aiohttp
from discord.ext import commands

from util.decorators import delete_original


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.trivia_messages = []
        self.new_trivia = []

    @commands.command(aliases=['porn'], hidden=True)
    @commands.is_nsfw()
    @delete_original()
    async def nsfw(self, ctx, *, query: str):
        """Get a random NSFW Gif via search query"""
        base_url = f'https://api.redgifs.com/v1/gfycats/search?search_text={query}&count=100'

        async with aiohttp.ClientSession() as session:
            async with session.get(base_url) as r:
                data = await r.json()
                if data['found'] > 0:
                    gifs = data['gfycats']
                    rand_gif = random.choice(gifs)
                    gif_link = rand_gif['gifUrl']
                    await ctx.send(gif_link)

def setup(bot):
    bot.add_cog(Fun(bot))
