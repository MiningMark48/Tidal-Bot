import copy

import discord
from discord.ext import commands

from util.data.guild_data import GuildData
from util.decorators import delete_original


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def set_currency(guild_id: str, user_id: str, amount: int):
        return GuildData(guild_id).economy.set(user_id, amount)

    @staticmethod
    def get_currency(guild_id: str, user_id: str):
        amount = GuildData(guild_id).economy.fetch_by_name(user_id)
        return amount if amount else 0

    def add_currency(self, guild_id: str, user_id: str, amount: int):
        current = self.get_currency(guild_id, user_id)
        new_amt = current + amount if current else amount
        return self.set_currency(guild_id, user_id, new_amt)

    def remove_currency(self, guild_id: str, user_id: str, amount: int):
        new_amt = self.get_currency(guild_id, user_id) - amount
        self.set_currency(guild_id, user_id, new_amt)
        return new_amt

    @commands.group()
    @commands.has_permissions(manage_guild=True)
    @delete_original()
    async def currency(self, ctx):
        """Admin commands for manipulating currency"""

        if ctx.invoked_subcommand is None:
            await ctx.send(f"Invalid subcommand! ")

            msg = copy.copy(ctx.message)
            msg.content = f"{ctx.prefix}help {ctx.command}"
            new_ctx = await self.bot.get_context(msg, cls=type(ctx))
            await self.bot.invoke(new_ctx)

    @currency.command(name="add")
    async def currency_add(self, ctx, user: discord.Member, amount: int):
        """Add currency to a user"""

        amt = self.add_currency(str(ctx.guild.id), str(user.id), amount)
        await ctx.send(f"Added **{amount}** to {user.display_name}. They now have **{amt}**.")

    @currency.command(name="get")
    async def currency_get(self, ctx, user: discord.Member):
        """Get a user's currency"""

        amt = self.get_currency(str(ctx.guild.id), str(user.id))
        await ctx.send(f"{user.display_name} has **{amt}**.")

    @currency.command(name="remove", aliases=["delete"])
    async def currency_remove(self, ctx, user: discord.Member, amount: int):
        """Remove currency from a user"""

        amt = self.remove_currency(str(ctx.guild.id), str(user.id), amount)
        await ctx.send(f"Removed **{amount}** from {user.display_name}. They now have **{amt}**.")

    @currency.command(name="set")
    async def currency_set(self, ctx, user: discord.Member, amount: int):
        """Set a user's currency"""

        self.set_currency(str(ctx.guild.id), str(user.id), amount)
        await ctx.send(f"Set {user.display_name}'s amount to **{amount}**.")


def setup(bot):
    bot.add_cog(Economy(bot))
