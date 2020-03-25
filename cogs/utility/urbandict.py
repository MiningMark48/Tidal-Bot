import html

import discord
import requests
from bs4 import BeautifulSoup as bs
from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # noinspection PyBroadException
    @commands.command(aliases=['urbandictionary', 'urbandict'])
    @commands.cooldown(1, 3.5)
    @commands.is_nsfw()
    async def urban(self, ctx, *, query: str):
        """
        Define a word from Urban Dictionary
        """
        async with ctx.typing():
            try:
                query = html.escape(query)
                base_url = f"https://www.urbandictionary.com/define.php?term={query}"

                r = requests.get(base_url, timeout=1)
                content = r.content
                soup = bs(content, 'html.parser')

                div_content = soup.find_all(id="content")[0]
                def_panel = div_content.find_all("div", class_="def-panel")[0]
                def_header = def_panel.find_all("div", class_="def-header")[0]
                word = def_header.find_all("a", class_="word")[0]
                word_text = str(word.get_text()).capitalize()
                meaning = def_panel.find_all("div", class_="meaning")[0]
                meaning_text = meaning.get_text()

                embed = discord.Embed(title=word_text, url=r.url)
                embed.description = f'{meaning_text[:1800]} {"..." if len(meaning_text) > 1800 else ""}'
                embed.set_footer(text="Fetched from Urban Dictionary")

                await ctx.send(embed=embed)

            except IndexError:
                await ctx.send("No search results found!")
            except Exception as e:
                await ctx.send(f"An error occurred!\n`{e}`")


def setup(bot):
    bot.add_cog(Fun(bot))
