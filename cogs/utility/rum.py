from discord.ext import commands

import util.servconf as sc


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def on_message(self, message):

        if not sc.get_v(str(message.guild.id), "rum_enabled"):
            return

        reaction_emoji = "📱"

        if message.author == self.bot.user:
            return

        if message.guild:
            mem = message.guild.get_member(message.author.id)
            channel = message.channel
            if mem:
                if mem.is_on_mobile():
                    await message.add_reaction(reaction_emoji)
                    async for lmsg in channel.history(limit=2):
                        if lmsg:
                            if lmsg.author == message.author and lmsg.id != channel.last_message.id:
                                await lmsg.remove_reaction(reaction_emoji, self.bot.user)

    @commands.command(name="togglerum", aliases=["togglemobileindicator", "toggleismobile"])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    async def toggle_rum(self, ctx):
        """Toggle the mobile indicator reaction (RUM: R U Mobile?)"""
        result = sc.toggle_b(str(ctx.guild.id), "rum_enabled")
        await ctx.send(f'**{"Enabled" if not result else "Disabled"}** the mobile indicator.')


def setup(bot):
    bot.add_cog(Moderation(bot))
