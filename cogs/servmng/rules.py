import re

import discord
from discord.ext import commands

from util.data.guild_data import GuildData


class ServerManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setrules", aliases=["rulesset"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    async def set_rules(self, ctx, *rules: str):
        """Set the rules for the server."""

        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.message.delete()

        rules_text = ""
        index = 1
        for r in rules:
            rules_text += f"{index}. {r}\n"
            index += 1

        GuildData(str(ctx.guild.id)).strings.set("server_rules", rules_text)
        await ctx.send(f'Rules set to: \n```\n{rules_text}\n```')

    @commands.command(aliases=["listrules", "ruleslist"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    async def rules(self, ctx, edit_mode=False):
        """
        Get the rules for the server.

        Can be set using 'setrules'
        """

        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.message.delete()

        result = GuildData(str(ctx.guild.id)).strings.fetch_by_name("server_rules")
        if result:
            if edit_mode:
                fin_l = str(result).split("\n")
                result = " ".join("\"{}\"".format(re.sub(r'^.*?\. ', '', f)) for f in fin_l if f != "")

            await ctx.send(f'**Server Rules:**\n```\n{result}\n```')
        else:
            await ctx.send("No server rules have been set!")


def setup(bot):
    bot.add_cog(ServerManagement(bot))
