import html

import aiohttp
import discord
import requests
from bs4 import BeautifulSoup as bs
from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # noinspection PyBroadException
    @commands.command(name="memesearch", aliases=['knowyourmeme', 'kym'])
    @commands.cooldown(1, 3.5)
    async def meme_search(self, ctx, *, query: str):
        """
        Lookup a meme on Know Your Meme
        """
        async with ctx.typing():
            try:
                query = html.escape(query)
                base_url = f"https://knowyourmeme.com/search"
                payload = {"q": query}
                headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) '
                                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                                         'Chrome/50.0.2661.102 '
                                         'Safari/537.36'}

                async with aiohttp.ClientSession() as session:
                    async with session.get(base_url, params=payload, headers=headers) as r:
                        content = await r.content.read()

                        soup = bs(content, 'html.parser')

                        tbody = soup.find_all("tbody", class_="entry-grid-body infinite")[0]
                        first_row = tbody.find_all("tr")[0]
                        top_result = first_row.find_all("td")[0].find_all("a")[0]
                        thumbnail_url = top_result.find_all("img")[0]['data-src']
                        result_url = f"https://knowyourmeme.com{top_result['href']}"

                        s_r = requests.get(result_url, headers=headers, timeout=3)
                        s_content = s_r.content
                        s_soup = bs(s_content, 'html.parser')

                        info_sect = s_soup.find_all("section", class_="info")[0]
                        title_text = info_sect.find_all("a")[0].get_text()

                        body_sect = s_soup.find_all("section", "bodycopy")[0]
                        desc = body_sect.find_all("p")[0]
                        desc_text = desc.get_text()

                        embed = discord.Embed(title=title_text, url=s_r.url, color=0x13133e)
                        embed.set_thumbnail(url=thumbnail_url)
                        embed.description = f'{desc_text[:1800]} {"..." if len(desc_text) > 1800 else ""}'
                        embed.set_footer(text="Fetched from Know Your Meme")

                        await ctx.send(embed=embed)

            except IndexError:
                await ctx.send("No search results found!")
            except Exception as e:
                await ctx.send(f"An error occurred!\n`{e}`")


def setup(bot):
    bot.add_cog(Fun(bot))
