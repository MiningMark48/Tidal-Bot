import discord
import json
import os.path as osp
import util.userconf as uc
from discord.ext import commands

class ServerManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["botfollow", "followmode"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def follow(self, ctx):
        """
        Receive bot updates.
        
        When following, you will receive DMs from the bot regarding
        information on bot updates, when the bot is going offline, etc.
        """

        result = not uc.get_v(str(ctx.author.id), "follow_mode")
        if result == None:
            result = True
        uc.set_kv(str(ctx.author.id), "follow_mode", bool(result))

        await ctx.send(f'{ctx.author.mention}, you are {"now" if result else "no longer"} in follow mode.')

def setup(bot):
    bot.add_cog(ServerManagement(bot))