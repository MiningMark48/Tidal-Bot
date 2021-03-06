from discord.ext import commands
import discord

import asyncio

from util.decorators import delete_original


class ServerManagement(commands.Cog, name="Server Management"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="temprole", aliases=["trole"])
    @commands.has_permissions(manage_roles=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    @delete_original()
    async def temp_role(self, ctx, user: discord.Member, role: str, minutes: int):
        """
        Assign a user a temporary role.

        Minutes Min: 1, Max: 60

        Note: If the bot goes offline/restarts, the role will not be cleared from the user.
        """

        minutes = max(1, min(minutes, 60))

        roles = list(filter(lambda r: r.name.lower() == role.lower(), await ctx.guild.fetch_roles()))
        if not roles:
            return await ctx.send("Role not found!")

        _role = roles[0]

        await user.add_roles(_role, reason=f"TempRole: {minutes} min")
        await ctx.send(f"{user.mention} has been given the *{_role}* role for **{minutes}** minute{'s' if minutes > 1 else ''}"
                       f" by {ctx.author.mention}.")

        await asyncio.sleep(minutes * 60)

        await user.remove_roles(_role, reason=f"TempRole: {minutes} min")


def setup(bot):
    bot.add_cog(ServerManagement(bot))
