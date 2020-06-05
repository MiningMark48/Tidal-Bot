from discord.ext import commands

from util.data.guild_data import GuildData


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def on_message(self, message):

        if not message.guild:
            return

        if not GuildData(str(message.guild.id)).booleans.fetch_by_name("rum_enabled"):
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
        result = GuildData(str(ctx.guild.id)).booleans.toggle_boolean("rum_enabled")
        await ctx.send(f'**{"Enabled" if result else "Disabled"}** the mobile indicator.')


def setup(bot):
    bot.add_cog(Utility(bot))
