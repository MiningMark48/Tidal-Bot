import discord
from discord.ext import commands

from util.data.user_data import UserData


class Preferences(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="botdms", aliases=["botdm"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def dms(self, ctx, *, enabled: bool):
        """
        Control whether or not the bot will DM you with certain commands/functions.

        Example: Disabling DMs will prevent bot from DMing reactor role gives/takes.

        Usage: botdms False
        """

        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.message.delete()

        result = UserData(str(ctx.author.id)).booleans.set("dm_enabled", enabled)

        await ctx.send(f"Bot DMs have been **{'enabled' if result else 'disabled'}**.", delete_after=10)


def setup(bot):
    bot.add_cog(Preferences(bot))
