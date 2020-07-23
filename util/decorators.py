import discord
from discord.ext import commands


def delete_original():
    async def predicate(ctx):
        if isinstance(ctx.message.channel, discord.TextChannel):
            await ctx.message.delete()
        return True

    return commands.check(predicate)
