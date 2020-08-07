from datetime import datetime

import aiohttp
import discord
from discord.ext import commands

from util.decorators import delete_original


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["leaderboard"])
    @commands.cooldown(1, 30, commands.BucketType.channel)
    @delete_original()
    async def activity(self, ctx, limit=750, today_only=False, include_bots=False):
        """
        View a leaderboard of the user with the most sent messages in a channel from a specified amount.

        Min: 10, Max: 2500
        """
        try:
            limit = max(min(limit, 2500), 10)

            embed = discord.Embed(title="Most Active Users", color=0xDB9066)
            embed.description = f"Fetching activity from *{limit}* messages."
            embed.timestamp = ctx.message.created_at
            embed.add_field(name="Today Only?", value="Yes" if today_only else "No")
            embed.add_field(name="Include Bots?", value="Yes" if include_bots else "No")

            og_msg = await ctx.send(embed=embed)

            activity = {}

            oldest = datetime.today()
            async for msg in ctx.channel.history(limit=limit):
                author = msg.author
                if not today_only or (today_only and str(msg.created_at.date()) == str(datetime.today().date())):
                    if not author.bot or include_bots:
                        if author not in activity:
                            activity.update({author: 1})
                        else:
                            activity.update({author: activity.get(author) + 1})
                        if msg.created_at < oldest:
                            oldest = msg.created_at

            activity = {k: v for k, v in sorted(activity.items(), key=lambda item: item[1], reverse=True)}
            if not today_only:
                embed.add_field(name="Since", value=oldest.strftime("%m/%d/%Y"))

            new_desc = ""
            index = 0
            for i in activity:
                if index <= 5:
                    amt = activity.get(i)
                    new_desc += f"**{index+1})** {i.mention}\n{amt} Message{'s' if amt != 1 else ''} Sent\n\n"
                index += 1

            new_desc += f"*{limit}* messages - *{ctx.channel.name}*"

            embed.description = new_desc
            await og_msg.edit(embed=embed)
        except discord.NotFound:
            await ctx.send("An error has occurred, please try again later. ")

    @commands.command()
    async def botinfo(self, ctx):
        """Miscellaneous bot information"""
        embed = discord.Embed(title="Bot Info", color=ctx.message.author.top_role.color)
        embed.add_field(name="Name", value=self.bot.user.name)
        embed.add_field(name="ID", value=self.bot.user.id)
        embed.add_field(name="Author", value="MiningMark48")
        embed.add_field(name="Library", value="discord.py")
        embed.add_field(name="Total Commands", value=str(len(self.bot.commands)))
        # embed.add_field(name="Current Activity", value=self.bot.user.activity)
        # embed.add_field(name="Command Key", value=self.bot.bot_key)
        try:
            await ctx.send(embed=embed)
        except discord.HTTPException:
            await ctx.send("Error sending embeded message, please try again later")

    @commands.command(aliases=["githubuser", "githubinfo"])
    async def github(self, ctx, user: str):
        """Look up information about a user on Github"""
        base_url = f"https://api.github.com/users/{user}"
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url) as r:
                data = await r.json()
        embed = discord.Embed(title=data["login"], color=ctx.message.author.top_role.color, url=data["html_url"])
        embed.add_field(name="Name", value=data["name"])
        embed.add_field(name="Company", value=data["company"])
        embed.add_field(name="Location", value=data["location"])
        embed.add_field(name="Bio", value=data["bio"], inline=False)
        embed.add_field(name="Website", value=data["blog"], inline=False)
        embed.add_field(name="Followers", value=data["followers"])
        embed.add_field(name="Following", value=data["following"])
        embed.add_field(name="Joined", value=data["created_at"][:-10])
        embed.set_thumbnail(url=data["avatar_url"])
        embed.set_footer(text=f"Github Information, requested by {ctx.author.name}")
        try:
            await ctx.send(embed=embed)
        except discord.HTTPException:
            await ctx.send("Error sending embeded message, please try again later")

    @commands.command(aliases=["serverinfo", "servinfo"])
    async def guildinfo(self, ctx):
        """Get information about the server"""
        embed = discord.Embed(title="Guild Info", color=ctx.message.author.top_role.color)
        embed.add_field(name="Name", value=ctx.guild.name)
        embed.add_field(name="ID", value=ctx.guild.id)
        embed.add_field(name="Owner", value=ctx.guild.owner.name)
        embed.add_field(name="Created on", value="--")
        embed.add_field(name="Users Joined", value=str(len(ctx.guild.members)))
        embed.add_field(name="Emote Amount", value=str(len(ctx.guild.emojis)))
        embed.add_field(name="Verified?", value="--")
        embed.add_field(name="Region", value=ctx.guild.region)
        embed.add_field(name="AFK Timeout", value=f'{ctx.guild.afk_timeout/60} minutes')
        embed.add_field(name="AFK Channel", value=ctx.guild.afk_channel)
        embed.set_thumbnail(url=f'https://cdn.discordapp.com/icons/{ctx.guild.id}/{ctx.guild.icon}.png')
        try:
            await ctx.send(embed=embed)
        except discord.HTTPException:
            await ctx.send("Error sending embeded message, please try again later")

    @commands.command(aliases=["meinfo", "whome"])
    async def selfinfo(self, ctx):
        """Get information about yourself"""
        embed = discord.Embed(title="Self Info", color=ctx.message.author.top_role.color)
        embed.add_field(name="Name", value=ctx.author.name)
        embed.add_field(name="ID", value=ctx.author.id)
        embed.add_field(name="Created", value=str(ctx.author.joined_at)[:-16])
        embed.add_field(name="Nick", value="--" if ctx.author.nick is None else ctx.author.nick)
        embed.add_field(name="Status", value=str(ctx.author.status).capitalize())
        embed.add_field(name="Mobile?", value="Yes" if ctx.author.is_on_mobile() else "No")
        embed.add_field(name="Activity", value=ctx.author.activity)
        embed.set_thumbnail(url=ctx.author.avatar_url)
        try:
            await ctx.send(embed=embed)
        except discord.HTTPException:
            await ctx.send("Error sending embeded message, please try again later")

    @commands.command(hidden=True, name="serverinvite", aliases=["invite"])
    async def server_invite(self, ctx):
        """Get a link to invite the bot to your server."""

        perms = 8
        # perms = 1043852400
        invite = discord.utils.oauth_url(client_id=self.bot.user.id, permissions=discord.Permissions(permissions=perms))

        await ctx.author.send(invite)

    @commands.command(aliases=["steamuser", "steaminfo"])
    async def steam(self, ctx, user: str):
        """Look up information about a user on Mixer"""
        base_url = f"https://playerdb.co/api/player/steam/{user}"
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url) as r:
                data = await r.json()

                if data["code"] != "player.found":
                    await ctx.send("User not found!")
                    return

                user_data = data["data"]
                player_data = user_data["player"]
                meta_data = player_data["meta"]

                # date = datetime.fromtimestamp(meta_data["timecreated"] / 1e3)

                embed = discord.Embed(title=player_data["username"], color=ctx.message.author.top_role.color,
                                      url=f"https://steamcommunity.com/id/{user}")

                embed.add_field(name="Username", value=player_data["username"])
                embed.add_field(name="Real Name", value=meta_data["realname"])
                embed.add_field(name="Country", value=meta_data["loccountrycode"])
                # embed.add_field(name="Date Created", value=str(date))
                status = meta_data["personastate"]
                embed.add_field(name="Status", value="Offline" if status == 0 else ("Online" if status == 1 else
                                                                                    ("Away" if status == 3 else "N/A")))
                embed.add_field(name="ID", value=player_data["id"])

                embed.set_thumbnail(url=player_data["avatar"])
                embed.set_footer(text=f"Steam Information, requested by {ctx.author.name}")
                try:
                    await ctx.send(embed=embed)
                except discord.HTTPException:
                    await ctx.send("Error sending embeded message, please try again later")

    @commands.command(name="tidalwave", aliases=["discord"])
    @delete_original()
    async def tidal_wave(self, ctx):
        """Get a link to the Tidal Wave Discord"""
        await ctx.send(f"{ctx.author.mention}, Here you go!\nhttps://discord.gg/SMCEXw5")

    @commands.command()
    @delete_original()
    async def trello(self, ctx):
        """Get a link to the Tidal Bot Trello"""
        await ctx.send(f"{ctx.author.mention}, Here you go!\nhttps://trello.com/b/U3TTk5Kc/tidal-bot")

    @commands.command(aliases=["userinfo"])
    @commands.guild_only()
    async def whois(self, ctx, user: discord.User):
        """Get information about another user"""
        embed = discord.Embed(title="User Info", color=ctx.message.author.top_role.color)
        embed.add_field(name="Name", value=user.name)
        embed.add_field(name="ID", value=user.id)
        embed.add_field(name="Created", value=str(user.created_at)[:-16])
        # embed.add_field(name="Display Name", value=user.display_name)
        # embed.add_field(name="Status", value=str(user.status).capitalize())
        # embed.add_field(name="Mobile?", value="Yes" if user.is_on_mobile() else "No")
        # embed.add_field(name="Activity", value=user.activity)
        embed.set_thumbnail(url=user.avatar_url)
        try:
            await ctx.send(embed=embed)
        except discord.HTTPException:
            await ctx.send("Error sending embeded message, please try again later")

    # @commands.command(aliases=["youtubeuser", "youtubeinfo"])
    # async def youtube(self, ctx, user: str):
    #     """Look up information about a user on YouTube"""
    #     base_url = f"https://www.googleapis.com/youtube/v3/channels?&key=AIzaSyBnt38rBPV1WAZGx6imcMvp0GuuQU15YKE" \
    #                f"&part=statistics,brandingSettings&forUsername={user}"
    #     url = requests.get(base_url, timeout=0.5)
    #     data = url.json()
    #
    #     embed = discord.Embed(title=data["items"][0]["brandingSettings"]["channel"]["title"],
    #                           color=ctx.message.author.top_role.color,
    #                           url=f"http://www.youtube.com/channel/{data['items'][0]['id']}")
    #     embed.add_field(name="Name", value=data["items"][0]["brandingSettings"]["channel"]["title"])
    #     embed.add_field(name="Subscribers", value=data["items"][0]["statistics"]["subscriberCount"])
    #     embed.add_field(name="Views", value=data["items"][0]["statistics"]["viewCount"])
    #     embed.add_field(name="Videos", value=data["items"][0]["statistics"]["videoCount"])
    #     embed.add_field(name="Description", value=data["items"][0]["brandingSettings"]["channel"]["description"],
    #                     inline=False)
    #     embed.set_footer(text=f"YouTube Information, requested by {ctx.author.name}")
    #     try:
    #         await ctx.send(embed=embed)
    #     except discord.HTTPException:
    #         await ctx.send("Error sending embeded message, please try again later")


def setup(bot):
    bot.add_cog(Info(bot))
