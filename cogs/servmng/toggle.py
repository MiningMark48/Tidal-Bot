import discord
import json
import os.path as osp
from util.servconf import toggle_string_array
from discord.ext import commands

class ServerManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["commandtoggle"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.guild_only()
    async def togglecommand(self, ctx, command: str):
        """Enable/Disable commands"""
        no_blacklist = ["togglecommand"]

        cmd = self.bot.get_command(command)
        if not cmd:
            return await ctx.send(f'`{command}` was not found as a valid command. Please try again!')
        if cmd.name in no_blacklist:
            return await ctx.send(f'You cannot disable `{cmd.name}`!')

        result = toggle_string_array(str(ctx.guild.id), cmd.name, "command_blacklist")

        await ctx.send(f'**{"Enabled" if result else "Disabled"}** the `{cmd.name}` command.')

def setup(bot):
    bot.add_cog(ServerManagement(bot))