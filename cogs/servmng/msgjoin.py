import discord
import json
import os.path as osp
import util.servconf as sc
from discord.ext import commands

class ServerManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setmsgjoin", aliases=["setjoinmsg"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.guild_only()
    async def set_message_join(self, ctx, *, msg: str):
        """Set a message to be sent to a user when they join the server."""
        await ctx.message.delete()

        sc.set_kv(str(ctx.guild.id), "join_message", msg)
        await ctx.send(f'Set join message to `{msg}`.')

    @commands.command(name="getmsgjoin", aliases=["getjoinmsg"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.guild_only()
    async def get_message_join(self, ctx):
        """Get the message to be sent to a user when they join the server."""
        await ctx.message.delete()

        msg = sc.get_v(str(ctx.guild.id), "join_message")
        if msg:
            await ctx.send(f'Current join message is `{msg}`.')
        else:
            await ctx.send(f'No message currently set!')

    @commands.command(name="clearmsgjoin", aliases=["clearjoinmsg", "delmsgjoin", "deljoinmsg"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.guild_only()
    async def clear_message_join(self, ctx):
        """Clear the message to be sent to a user when they join the server."""
        await ctx.message.delete()

        sc.del_v(str(ctx.guild.id), "join_message")
        await ctx.send(f'Deleted join message.')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        msg = sc.get_v(str(member.guild.id), "join_message")
        if msg:
            await member.send(f'{msg}')

def setup(bot):
    bot.add_cog(ServerManagement(bot))