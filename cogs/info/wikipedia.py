import re

import aiohttp
import discord
import requests
from bs4 import BeautifulSoup as bs
from discord.ext import commands


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # noinspection PyBroadException
    @commands.command(aliases=['wiki', 'wp'])
    @commands.cooldown(1, 3.5)
    async def wikipedia(self, ctx, *, query: str):
        """
        Search Wikipedia
        """
        async with ctx.typing():
            try:
                base_url = "https://en.wikipedia.org/w/index.php"
                payload = {"search": query, "cirrusUserTesting": "control", "sort": "relevance", "title": "Special:Search",
                           "profile": "advanced", "fulltext": 1, "advancedSearch-current": "%7B%7D", "ns0": 1}

                async with aiohttp.ClientSession() as session:
                    async with session.get(base_url, params=payload) as r:
                        content = await r.content.read()

                        soup = bs(content, 'html.parser')
                        search_results = soup.find("ul", class_="mw-search-results")
                        top_result = search_results.find_all_next("li")[0]
                        result_link_div = top_result.find_all_next("div")[0]
                        result_link_a = result_link_div.find("a")
                        result_link = "https://en.wikipedia.org{}".format(result_link_a['href'])

                        s_r = requests.get(result_link, timeout=1)
                        s_content = s_r.content
                        s_soup = bs(s_content, 'html.parser')
                        s_output = s_soup.find("div", class_="mw-parser-output")
                        s_p_no_class = s_output.find_all_next("p", attrs={'class': None})[0]
                        s_p_desc = s_p_no_class.get_text()[:500]

                        s_meta_covimg = s_soup.find_all("meta", property=re.compile(r'^og:image'))

                        embed = discord.Embed(title=result_link_a['title'], url=s_r.url)
                        embed.description = f'{s_p_desc}...'
                        embed.set_footer(text="Fetched from Wikipedia")

                        if s_meta_covimg:
                            s_covimg_link = s_meta_covimg[0]['content']
                            embed.set_image(url=s_covimg_link)

                        await ctx.send(embed=embed)

            except IndexError:
                await ctx.send("No search results found!")
            except Exception as e:
                await ctx.send(f"An error occurred!\n`{e}`")


def setup(bot):
    bot.add_cog(Info(bot))
