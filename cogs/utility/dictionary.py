import discord
import requests
from bs4 import BeautifulSoup as bs
from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # noinspection PyBroadException
    @commands.command(aliases=['define'])
    @commands.cooldown(1, 3.5)
    async def dictionary(self, ctx, *, query: str):
        """
        Define a word
        """
        async with ctx.typing():
            try:
                base_url = f"https://www.merriam-webster.com/dictionary/{query}"

                r = requests.get(base_url, timeout=1)
                content = r.content
                soup = bs(content, 'html.parser')

                word = soup.find_all("h1", class_="hword")[0]
                word_text = word.get_text()

                dict_entry_div = soup.find_all(id="dictionary-entry-1")[0]
                dict_entry = dict_entry_div.find_all("div", class_="vg")[0]
                dict_entry_sect = dict_entry.find_all("div", attrs={"class": "sb"})
                dict_entry_text = "\n\n".join(e.get_text() for e in dict_entry_sect)[:1000]

                embed = discord.Embed(title=word_text, url=r.url)
                embed.description = f'{dict_entry_text}...'
                embed.set_footer(text="Fetched from Merriam Webster")

                await ctx.send(embed=embed)

            except IndexError:
                await ctx.send("No search results found!")
            except Exception as e:
                await ctx.send(f"An error occurred!\n`{e}`")


def setup(bot):
    bot.add_cog(Fun(bot))
