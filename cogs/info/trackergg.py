import random
import itertools
import aiohttp
import discord
from discord.ext import commands

from util import BotConfig


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = BotConfig().get_api_key('trackergg')

    @commands.command(name="apexlegends", aliases=["apex"])
    @commands.cooldown(3, 5, commands.BucketType.user)
    async def tracker_apex_legends(self, ctx, username: str, platform="pc"):
        """
        Apex Legends Tracker: Gets stats for an Apex Legends account

        Platforms: PC, PS, XBOX
        """

        async with ctx.typing():

            un = username.replace("_", "%5F")

            platform = platform.lower()
            platform_num = 5
            if platform == "xbox":
                platform_num = 1
            elif platform == "ps":
                platform_num = 2
            else:
                platform = "pc"

            try:
                base_url = f"https://public-api.tracker.gg/apex/v1/standard/profile/{platform_num}/{un}"
                headers = {"TRN-Api-Key": self.api_key}

                async with aiohttp.ClientSession() as session:
                    async with session.get(base_url, headers=headers) as r:
                        data = await r.json()

                        if "errors" in data:
                            return await ctx.send("Invalid username! \n`{}` can not be found on `{}`."
                                                  .format(username, platform))

                        data_legends = data["data"]["children"]
                        data_stats = data["data"]["stats"]

                        sort_by = "Kills"
                        legends_data = {}
                        for legend in data_legends:
                            lgnd = {sort_by: 0.0}
                            for stat in legend["stats"]:
                                lgnd[stat["metadata"]["name"]] = stat["value"]
                            legends_data[legend["metadata"]["legend_name"]] = lgnd

                        legends_data = dict(sorted(legends_data.items(),
                                                   key=lambda x: int(x[1][sort_by]), reverse=True))

                        embed = discord.Embed(title=f"Apex Legends Statistics: {username} ({platform.upper()})",
                                              color=0xc83031)
                        # embed.set_thumbnail(url=data_legends[0]["metadata"]["icon"])
                        embed.set_thumbnail(url=random.choice(data_legends)["metadata"]["icon"])
                        embed.description = "__**User Stats**__\n"

                        embed.description += "\n".join(f"{stat['metadata']['name']}: {stat['displayValue']}"
                                                       for stat in data_stats[:3])
                        embed.description += "\n\n__**Top Legend Stats**__\n"

                        for legend in dict(itertools.islice(legends_data.items(), 3)):
                            data_legend_name = legend
                            data_legend_stats = legends_data[legend]

                            embed.description += f"**{data_legend_name}**\n"
                            embed.description += "\n".join(f"> {stat}: {round(data_legend_stats[stat]):,}"
                                                           for stat in data_legend_stats)
                            embed.description += "\n\n"

                        embed.set_footer(text="[WIP] | Data Provided by trackers.gg")

                        await ctx.send(embed=embed)

            except IndexError:
                await ctx.send("No search results found!")
            # except Exception as e:
            #     await ctx.send(f"An error occurred!\n`{e}`")


def setup(bot):
    bot.add_cog(Utility(bot))
