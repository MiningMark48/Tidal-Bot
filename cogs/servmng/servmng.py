from discord.ext import commands

import util.servconf as sc
import util.userconf as uc
from util.servconf import toggle_string_array


class ServerManagement(commands.Cog, name="Server Management"):
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
        if result is None:
            result = True
        uc.set_kv(str(ctx.author.id), "follow_mode", bool(result))

        await ctx.send(f'{ctx.author.mention}, you are {"now" if result else "no longer"} in follow mode.')

    @commands.command(aliases=["changeprefix"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def setprefix(self, ctx, prefix: str):
        """Change the bot prefix for the server"""

        sc.set_kv(str(ctx.guild.id), "prefix", prefix)
        await ctx.send(f'Changed the server prefix to `{prefix}`.')

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

    @commands.group(name="joinmessage", aliases=["joinmsg"])
    async def join_msg(self, ctx):
        """Join message is a message to be sent to a user when they join the server."""
        pass

    @join_msg.command(name="set")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.guild_only()
    async def set_message_join(self, ctx, *, msg: str):
        """Set a message to be sent to a user when they join the server."""
        await ctx.message.delete()

        sc.set_kv(str(ctx.guild.id), "join_message", msg)
        await ctx.send(f'Set join message to `{msg}`.')

    @join_msg.command(name="get")
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

    @join_msg.command(name="clear")
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
