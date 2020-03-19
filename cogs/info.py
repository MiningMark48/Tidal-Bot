import discord
import requests
from discord.ext import commands


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def botinfo(self, ctx):
        """Miscellaneous bot information"""
        embed = discord.Embed(title="Bot Info", color=ctx.message.author.top_role.color)
        embed.add_field(name="Name", value=self.bot.user.name)
        embed.add_field(name="ID", value=self.bot.user.id)
        embed.add_field(name="Author", value="MiningMark48")
        embed.add_field(name="Library", value="discord.py")
        # embed.add_field(name="Current Activity", value=self.bot.user.activity)
        # embed.add_field(name="Command Key", value=self.bot.bot_key)
        try:
            await ctx.send(embed=embed)
        except discord.HTTPException:
            await ctx.send("Error sending embeded message, please try again later")

    @commands.command(aliases=["covid", "covid19", "corona"])
    async def coronavirus(self, ctx):
        """Get information regarding COVID-19, Coronavirus"""
        await ctx.send(
            "For information regarding COVID-19, better known as the Coronavirus, please visit "
            "<https://coronavirus.gov/>.\n\n"
            "Be safe, protect yourself as well as others!"
        )

    @commands.command(aliases=["githubuser", "githubinfo"])
    async def github(self, ctx, user: str):
        """Look up information about a user on Github"""
        base_url = f"https://api.github.com/users/{user}"
        url = requests.get(base_url, timeout=0.5)
        data = url.json()
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

    @commands.command(aliases=["mixeruser", "mixerinfo"])
    async def mixer(self, ctx, user: str):
        """Look up information about a user on Mixer"""
        base_url = f"https://mixer.com/api/v1/channels/{user}"
        url = requests.get(base_url, timeout=0.5)
        data = url.json()
        embed = discord.Embed(title=data["token"], color=ctx.message.author.top_role.color,
                              url=f"https://mixer.com/{user}")
        embed.add_field(name="Stream Title", value=data["name"], inline=False)
        embed.add_field(name="Game", value=data["type"]["name"], inline=False)
        embed.add_field(name="Is Online?", value="Yes" if data["online"] else "No")
        embed.add_field(name="Is Partnered?", value="Yes" if data["partnered"] else "No")
        embed.add_field(name="Audience", value=data["audience"])
        embed.add_field(name="Member Since", value=data["createdAt"][:-14])
        embed.add_field(name="Last Updated", value=data["updatedAt"][:-14])
        embed.add_field(name="Level", value=data["user"]["level"])
        embed.add_field(name="Sparks", value=data["user"]["sparks"])
        embed.add_field(name="Followers", value=data["numFollowers"])
        embed.add_field(name="Total Viewers", value=data["viewersTotal"])
        embed.add_field(name="Current Viewers", value=data["viewersCurrent"])
        embed.add_field(name="Is Interactive?", value="Yes" if data["interactive"] else "No")
        embed.add_field(name="VODs Enabled?", value="Yes" if data["vodsEnabled"] else "No")

        embed.set_thumbnail(url=data["user"]["avatarUrl"])
        embed.set_footer(text=f"Mixer Information, requested by {ctx.author.name}")
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
        embed.add_field(name="Nick", value="--" if ctx.author.nick == None else ctx.author.nick)
        embed.add_field(name="Status", value=str(ctx.author.status).capitalize())
        embed.add_field(name="Mobile?", value="Yes" if ctx.author.is_on_mobile() else "No")
        embed.add_field(name="Activity", value=ctx.author.activity)
        embed.set_thumbnail(url=ctx.author.avatar_url)
        try:
            await ctx.send(embed=embed)
        except discord.HTTPException:
            await ctx.send("Error sending embeded message, please try again later")

    @commands.command(hidden=True, aliases=["invite"])
    async def serverinvite(self, ctx):
        await ctx.author.send(
            f'https://discordapp.com/oauth2/authorize?&client_id={self.bot.user.id}&scope=bot&permissions=70351936')

    @commands.command(name="getdocs", aliases=["docs", "documentation"])
    async def get_docs(self, ctx):
        """Returns a link to bot documentation"""
        await ctx.send("http://bit.ly/tidalbotdocs")

    # @commands.command(aliases=["twitchuser", "twitchinfo"])
    # async def twitch(self, ctx, user: str):
    #     """[WIP] Look up information about a user on Twitch"""
    #     base_url = f"https://mixer.com/api/v1/channels/{user}"
    #     with urllib.request.urlopen(base_url) as url:
    #         data = json.loads(url.read().decode())
    #         embed = discord.Embed(title=data["token"], color=ctx.message.author.top_role.color, url=f"https://mixer.com/{user}")
    #         embed.add_field(name="Stream Title", value=data["name"], inline=False)
    #         embed.set_thumbnail(url=data["user"]["avatarUrl"])
    #         embed.set_footer(text=f"Mixer Information, requested by {ctx.author.name}")
    #         try:
    #             await ctx.send(embed=embed)
    #         except discord.HTTPException:
    #             await ctx.send("Error sending embeded message, please try again later")

        await ctx.send("This command is a work-in-progress!")

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
