import json

import discord
import praw
import prawcore
import requests
from discord.ext import commands


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("config.json", 'r') as file:
            data = json.load(file)["reddit"]
            self.reddit = praw.Reddit(
                client_id=data["client_id"],
                client_secret=data["client_secret"],
                user_agent=data["user_agent"]
            )

    # noinspection PyBroadException
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def reddit(self, ctx, subreddit="all"):
        try:
            r = self.reddit
            sr = r.subreddit(subreddit)
            sr_rand = sr.random()
            link = f"https://www.reddit.com{sr_rand.permalink}"

            if isinstance(ctx.channel, discord.TextChannel):
                await ctx.message.delete()
                try:
                    if sr.over18 and not ctx.channel.is_nsfw():
                        await ctx.send("Channel must be NSFW to view that subreddit!")
                except prawcore.exceptions.NotFound:
                    pass

            embed = discord.Embed(title=sr_rand.title[:256], url=link, color=0xFF4500)
            embed.set_author(name=f"/u/{sr_rand.author.name}")
            embed.description = sr_rand.selftext[:500]
            embed.set_footer(text=f"/r/{sr.display_name}")

            if is_url_image(sr_rand.url):
                embed.set_image(url=sr_rand.url)

            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"An error has occurred!\n`{e}`")


def is_url_image(image_url):
    image_formats = ("image/png", "image/jpeg", "image/jpg", "image/gif")
    r = requests.head(image_url)

    try:
        return r.headers["content-type"] in image_formats
    except KeyError:
        return False


def setup(bot):
    bot.add_cog(Utility(bot))
