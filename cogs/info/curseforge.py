import cloudscraper
from bs4 import BeautifulSoup as bs

import discord
from discord.ext import commands

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['cf', 'curse'])
    @commands.cooldown(2, 30)
    async def curseforge(self, ctx, *, username: str):
        """
        Get Curseforge Project Stats
        """
        async with ctx.typing():
            try:
                base_url = f"https://www.curseforge.com/members/{username}/projects"

                scraper = cloudscraper.create_scraper()
                content = scraper.get(base_url).text

                soup = bs(content, 'html.parser')

                listing_cont = soup.find(
                    "div", class_="listing-container listing-container-ul")

                listings = listing_cont.find_all_next(
                    "li", class_="latest-post-item")

                user_projects = dict()

                for listing in listings:
                    details = listing.find_all(
                        "div", class_="project-details")[0]

                    project_link = "https://www.curseforge.com/{}".format(details.find_all("a")[0]['href'])
                    
                    project_content = scraper.get(project_link).text
                    soup = bs(project_content, 'html.parser')

                    about_col = soup.find_all("div", class_="pb-4 border-b border-gray--100")[0]
                    about_col_info = about_col.find_all("div", class_="flex flex-col mb-3")[0]
                    downloads_div = about_col_info.find_all("div", class_="w-full flex justify-between")[3]
                    downloads_elm = downloads_div.find_all("span")[1]
                    downloads_text = downloads_elm.text

                    project_name = details.find_all("a")[0].text

                    user_projects.update({project_name: downloads_text})

                embed = discord.Embed(title=f"CurseForge: {username}", url=base_url, color=0x503483)
                embed.timestamp = ctx.message.created_at

                total_downloads = 0
                for proj in sorted(user_projects):
                    downloads = user_projects[proj]
                    embed.add_field(name=proj, value=f"{downloads} downloads")

                    total_downloads += int(downloads.replace(",", ""))
                
                embed.description = f"**Total Downloads:**\n{total_downloads:,}\n-"

                await ctx.send(embed=embed)

            except (IndexError, AttributeError):
                await ctx.send("No search results found!")
            except Exception as e:
                await ctx.send(f"An error occurred!\n`{e}`")


def setup(bot):
    bot.add_cog(Info(bot))
