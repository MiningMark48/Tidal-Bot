import discord
from discord.ext import commands

from util.data.guild_data import GuildData


class ServerManagement(commands.Cog, name="Server Management"):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="reactor", aliases=["reactionroles"])
    async def reactor(self, ctx):
        """
        Reactor allows users to react to a message to get assigned a specific role.

        Note: This feature is experimental and susceptible to faults.
        """
        pass

    @reactor.command(name="add")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.guild_only()
    async def reactor_add(self, ctx, message_id: int, role_id: int, emoji: str):
        """Add a reactor message."""
        await ctx.message.delete()

        if not ctx.guild.get_role(role_id):
            await ctx.send("Role not found!", delete_after=10)
            return

        GuildData(str(ctx.guild.id)).reactors.insert(message_id, role_id, emoji)

        await ctx.send(f'Reactor has been set.', delete_after=10)

        msg = await ctx.fetch_message(message_id)
        await msg.add_reaction(emoji)

    @reactor.command(name="get")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.guild_only()
    async def reactor_get(self, ctx):
        """Get the available reactors."""
        await ctx.message.delete()

        reactors = GuildData(str(ctx.guild.id)).reactors.fetch_all()

        embed = discord.Embed(title="Reactors")
        for r in reactors:
            embed.add_field(name="Message ID", value=r[1])
            embed.add_field(name="Role ID", value=r[2])
            embed.add_field(name="Emoji", value=f"{r[3]}\n--", inline=False)
        embed.set_footer(text=f"Total Amount: {len(reactors)}")

        if reactors:
            await ctx.send(embed=embed)
        else:
            await ctx.send(f'No reactors currently set!', delete_after=10)

    @reactor.command(name="delete")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.guild_only()
    async def reactor_delete(self, ctx, message_id: int):
        """Delete all reactors on a specific message."""
        await ctx.message.delete()

        data_reactors = GuildData(str(ctx.guild.id)).reactors
        reactors = data_reactors.fetch_all()

        if reactors is None or len(reactors) == 0:
            await ctx.send("No reactors currently set!", delete_after=10)
            return

        result = data_reactors.delete(message_id)
        if result:
            await ctx.send("Reactors removed from message.", delete_after=10)
        else:
            await ctx.send("Reactor not found.", delete_after=10)

    @reactor.command(name="clearall")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.guild_only()
    async def reactor_clear_all(self, ctx):
        """Clear all reactors."""
        await ctx.message.delete()

        GuildData(str(ctx.guild.id)).reactors.delete_all()

        await ctx.send("All reactors deleted.")

    @commands.Cog.listener("on_raw_reaction_add")
    async def on_raw_reaction_add(self, payload):
        await self.reaction_handle(payload, add_mode=True)

    @commands.Cog.listener("on_raw_reaction_remove")
    async def on_raw_reaction_remove(self, payload):
        await self.reaction_handle(payload, add_mode=False)

    async def reaction_handle(self, payload, add_mode: bool):

        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        user = guild.get_member(payload.user_id)
        rmsg = await channel.fetch_message(payload.message_id)

        if user == self.bot.user:
            return

        reactors = GuildData(str(guild.id)).reactors.fetch_all()
        reactors_filtered = filter(lambda r: rmsg.id == r[1], reactors)
        list_reactors = list(reactors_filtered)

        if len(list_reactors) > 0:
            for reac in list_reactors:
                re_msg_id = reac[1]
                re_role_id = reac[2]
                re_emoji = reac[3]

                reaction_emoji = str(payload.emoji)
                if reaction_emoji == re_emoji:
                    role = guild.get_role(re_role_id)
                    if add_mode:
                        await user.add_roles(role, reason=f"Reacted: {re_msg_id}")
                        await user.send(f"**Role Added**\nYou have been given the role *{role.name}* in *{guild.name}*"
                                        f" by reacting.")
                    else:
                        await user.remove_roles(role, reason=f"Un-Reacted: {re_msg_id}")
                        await user.send(f"**Role Removed**\nYou have gotten the role *{role.name}* removed in "
                                        f"*{guild.name}* by un-reacting.")

    @commands.Cog.listener("on_raw_message_delete")
    async def on_raw_message_delete(self, payload):
        guild = self.bot.get_guild(payload.guild_id)

        reactors = GuildData(str(guild.id)).reactors
        if not reactors.fetch_all():
            return

        reactors.delete(payload.message_id)


def setup(bot):
    bot.add_cog(ServerManagement(bot))
