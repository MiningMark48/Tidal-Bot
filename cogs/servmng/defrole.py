import copy

from discord.ext import commands

from util.data.guild_data import GuildData


class ServerManagement(commands.Cog, name="Server Management"):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="defrole", aliases=["defaultrole"])
    async def def_role(self, ctx):
        """
        Default role is a role to be added to a user when they join the server.
        Only one role can be set.
        """

        if ctx.invoked_subcommand is None:
            await ctx.send(f"Invalid subcommand! ")

            msg = copy.copy(ctx.message)
            msg.content = f"{ctx.prefix}help {ctx.command}"
            new_ctx = await self.bot.get_context(msg, cls=type(ctx))
            await self.bot.invoke(new_ctx)

    @def_role.command(name="set")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.guild_only()
    async def set_role_join(self, ctx, *, role_id: int):
        """Set a role to be added to a user when they join the server."""
        await ctx.message.delete()

        if not ctx.guild.get_role(role_id):
            await ctx.send("Role not found!", delete_after=10)
            return

        GuildData(str(ctx.guild.id)).strings.set("join_role", role_id)

        role = ctx.guild.get_role(role_id)
        await ctx.send(f'Set join role to `{role}`.')

    @def_role.command(name="get")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.guild_only()
    async def get_role_join(self, ctx):
        """Get the role to be added to a user when they join the server."""
        await ctx.message.delete()

        role_id = GuildData(str(ctx.guild.id)).strings.fetch_by_name("join_role")
        if role_id:
            role = ctx.guild.get_role(int(role_id))
            await ctx.send(f'Current join role is `{role}`.')
        else:
            await ctx.send('No role is currently set!')

    @def_role.command(name="clear")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.guild_only()
    async def clear_role_join(self, ctx):
        """Clear the role to be added to a user when they join the server."""
        await ctx.message.delete()

        GuildData(str(ctx.guild.id)).strings.delete("join_role")
        await ctx.send('Deleted join role.')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        role_id = GuildData(str(member.guild.id)).strings.fetch_by_name("join_role")
        if role_id:
            role = member.guild.get_role(int(role_id))
            if role:
                await member.add_roles(role)


def setup(bot):
    bot.add_cog(ServerManagement(bot))
