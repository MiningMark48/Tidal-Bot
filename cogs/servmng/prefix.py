import discord
import json
import os.path as osp
import util.servconf as sc
from discord.ext import commands

class ServerManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["changeprefix"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def setprefix(self, ctx, prefix: str):
        """Change the bot prefix for the server"""

        sc.set_kv(str(ctx.guild.id), "prefix", prefix)
        await ctx.send(f'Changed the server prefix to `{prefix}`.')

def setup(bot):
    bot.add_cog(ServerManagement(bot))