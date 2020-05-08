import aiohttp

import discord
from bs4 import BeautifulSoup as bs
from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(2, 2.5)
    async def xkcd(self, ctx):
        """
        Get a random XKCD comic
        """
        async with ctx.typing():
            rand_comic_url = "https://c.xkcd.com/random/comic/"

            async with aiohttp.ClientSession() as session:
                async with session.get(rand_comic_url) as r:
                    content = await r.content.read()

                    soup = bs(content, 'html.parser')
                    comic_div = soup.find(id='comic')
                    comic_img = comic_div.find_all_next("img")[0]
                    comic_src = "https:{}".format(comic_img['src'])

                    embed = discord.Embed(title=comic_img['alt'], description=comic_img['title'], url=str(r.url))
                    embed.set_image(url=comic_src)
                    embed.set_footer(text="Fetched from xkcd.com")
                    await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Fun(bot))
