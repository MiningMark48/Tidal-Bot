import aiohttp
import random
import re
from bs4 import BeautifulSoup as bs

import discord
from discord.ext import commands
from discord import Color

from util.decorators import delete_original


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def find_urls(self, string):
        regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        url = re.findall(regex, string)       
        return [x[0] for x in url]


    @commands.command(name="celebbday", aliases=["celebbirthday", "famousbday", "famousbirthday"])
    @commands.cooldown(1, 3)
    @delete_original()
    async def celeb_bday(self, ctx, month: int, day: int):
        """
        Get a random celebrity that has the same birthday as a specific date.
        """

        async with ctx.typing():

            months = {
                1: "january", 2: "february", 3: "march", 4: "april", 5: "may", 
                6: "june", 7: "july", 8: "august", 9: "september", 10: "october", 
                11: "november", 12: "december"
            }

            query = f"{months[month]}{day}"

            try:
                base_url = f"https://www.famousbirthdays.com/{query}.html"

                async with aiohttp.ClientSession() as session:
                    async with session.get(base_url) as r:
                        content = await r.content.read()

                        soup = bs(content, 'html.parser')

                        people_list_div = soup.find_all("div", class_="people-list")[0]
                        people_list_row = people_list_div.find_all("div", class_="row")[1]
                        people_list = people_list_row.find_all("a", class_="face person-item clearfix")

                        people = []
                        for person in people_list: 
                            person_info = person.find_all("div", class_="info")[0]
                            person_info_name = person_info.find_all("div", class_="name")[0]
                            person_info_title = person_info.find_all("div", class_="title")[0]
                            
                            name = str(person_info_name.get_text()).replace("\n", "")
                            title = str(person_info_title.get_text()).replace("\n", "")
                            picture_url = self.find_urls(person["style"])[0]

                            people.append({"name": name, "title": title, "picture_url": picture_url})

                        rand_person = random.choice(people)

                        embed = discord.Embed(title=f"Celebrity Birthday: {months[month].capitalize()} {day}", color=Color.dark_theme())
                        embed.set_thumbnail(url=rand_person["picture_url"])
                        embed.add_field(name="Celebrity", value=rand_person["name"])
                        embed.add_field(name="Title", value=rand_person["title"])
                        embed.set_footer(text="Fetched from Famous Birthdays")

                        await ctx.send(embed=embed)

            except IndexError:
                await ctx.send("No search results found!")
            except Exception as e:
                await ctx.send(f"An error occurred!\n`{e}`")


def setup(bot):
    bot.add_cog(Info(bot))
