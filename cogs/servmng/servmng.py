import sqlalchemy.exc
from discord.ext import commands

from util.data.guild_data import GuildData


class ServerManagement(commands.Cog, name="Server Management"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="commandblacklist", aliases=["togglecommand", "blacklistcommand"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.guild_only()
    async def command_blacklist(self, ctx, command: str, value=True):
        """Enable/Disable commands"""
        no_blacklist = ["commandblacklist"]

        cmd = self.bot.get_command(command)
        if not cmd:
            return await ctx.send(f'`{command}` was not found as a valid command. Please try again!')
        if cmd.name in no_blacklist:
            return await ctx.send(f'You cannot disable `{cmd.name}`!')

        data = GuildData(str(ctx.guild.id)).disabled_commands
        if value:
            try:
                data.insert(cmd.name)
            except sqlalchemy.exc.IntegrityError:
                await ctx.send("Command already disabled!")
                return
        else:
            data.delete(cmd.name)

        await ctx.send(f'**{"Enabled" if not value else "Disabled"}** the `{cmd.name}` command.')

    @commands.command(aliases=["changeprefix"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def setprefix(self, ctx, prefix: str):
        """Change the bot prefix for the server"""

        GuildData(str(ctx.guild.id)).strings.set("prefix", prefix)
        await ctx.send(f'Changed the server prefix to `{prefix}`.')

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

        GuildData(str(ctx.guild.id)).strings.set("join_message", msg)
        await ctx.send(f'Set join message to `{msg}`.')

    @join_msg.command(name="get")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.guild_only()
    async def get_message_join(self, ctx):
        """Get the message to be sent to a user when they join the server."""
        await ctx.message.delete()

        msg = GuildData(str(ctx.guild.id)).strings.fetch_by_name("join_message")
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

        GuildData(str(ctx.guild.id)).strings.delete("join_message")
        await ctx.send(f'Deleted join message.')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        msg = GuildData(str(member.guild.id)).strings.fetch_by_name("join_message")
        if msg:
            await member.send(f'{msg}')


def setup(bot):
    bot.add_cog(ServerManagement(bot))
