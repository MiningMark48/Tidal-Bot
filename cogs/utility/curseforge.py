import requests
from bs4 import BeautifulSoup as bs
from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # noinspection PyBroadException
    @commands.command(aliases=['cf', 'curse'])
    @commands.cooldown(1, 3.5)
    async def curseforge(self, ctx, *, username: str):
        """
        Get Curseforge Project Stats
        """
        async with ctx.typing():
            try:
                base_url = f"https://www.curseforge.com/members/{username}/projects"

                s = requests.Session()
                r = s.get(base_url)
                cookies = dict(r.cookies)
                r = s.post(base_url, verify=False, cookies=cookies)
                content = r.content
                soup = bs(content, 'html.parser')

                print(r.url)

                await ctx.send(f"```html\n{content[:1500]}```")

                listing_cont = soup.find("div", class_="listing-container listing-container-ul")

                print(listing_cont)

                listings = listing_cont.find_all_next("li", class_="latest-post-item")
                listing_links = []
                for listing in listings:
                    details = listing.find_all("div", class_="project-details")[0]
                    project_link = details.find_all("a")[0]['href']
                    listing_links.append(project_link)

                print(listing_links)

                # embed = discord.Embed(title=result_link_a['title'], url=s_r.url)
                # embed.description = f'{s_p_desc}...'
                # embed.set_footer(text="Fetched from Wikipedia")

                # await ctx.send(embed=embed)

            except IndexError:
                await ctx.send("No search results found!")
            except Exception as e:
                await ctx.send(f"An error occurred!\n`{e}`")


def setup(bot):
    bot.add_cog(Fun(bot))
