import copy
import typing
import datetime

import discord
from discord.ext import commands, tasks
from util.data.user_data import UserData


class Birthdays(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="birthday", aliases=["bday"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def birthday(self, ctx):
        """
        Allows users to set their birthdays
        """

        if ctx.invoked_subcommand is None:
            await ctx.send(f"Invalid subcommand! ")

            msg = copy.copy(ctx.message)
            msg.content = f"{ctx.prefix}help {ctx.command}"
            new_ctx = await self.bot.get_context(msg, cls=type(ctx))
            await self.bot.invoke(new_ctx)

    @birthday.command(name="set")
    @commands.guild_only()
    async def set_birthday(self, ctx, month: int, day: int):
        """
        Set your birthday.
        """

        # TODO: Add better date validity checking

        if month > 12 or month < 1:
            return await ctx.send("Invalid month! Must be between 1 and 12.")
        
        if day > 31 or day < 1:
            return await ctx.send("Invalid day! Must be between 1 and 31.")

        bday = f"{month}/{day}"

        UserData(str(ctx.author.id)).strings.set("birthday", bday)
        await ctx.send(f'Set your birthday to `{bday}`.')

    @birthday.command(name="get")
    @commands.guild_only()
    async def get_birthday(self, ctx, user: typing.Optional[discord.User]):
        """
        Get your or another user's birthday.
        """

        if not user:
            user = ctx.author

        bday = UserData(str(user.id)).strings.fetch_by_name("birthday")

        if bday:
            await ctx.send(f"**{user.display_name}**'s birthday is currently set to `{bday}`.")
        else:
            await ctx.send(f"**{user.display_name}**'s birthday is not currently set.")

    @birthday.command(name="del", aliases=["delete", "clear"])
    @commands.guild_only()
    async def del_birthday(self, ctx, user: typing.Optional[discord.User]):
        """
        Delete your birthday.
        """

        UserData(str(user.id)).strings.delete("birthday")
        await ctx.send('Your birthday was deleted.')


def setup(bot):
    bot.add_cog(Birthdays(bot))
