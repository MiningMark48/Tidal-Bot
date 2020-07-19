import discord
from discord.ext import commands


class Background(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_command")
    async def on_command(self, ctx):
        if not ctx.guild:
            return

        try:

            webhook = discord.utils.find(lambda w: (isinstance(w, discord.Webhook) and w.name == "tb-log"),
                                         await ctx.guild.webhooks())
            if webhook:
                embed = discord.Embed(title=ctx.command.name,
                                      color=ctx.message.author.top_role.color
                                      if hasattr(ctx.message.author, 'top_role') else 0x000000)
                embed.timestamp = ctx.message.created_at
                embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
                message_content = ctx.message.content
                embed.description = f'{message_content[:100]}...' if len(message_content) > 100 else message_content
                embed.add_field(name="Message Link", value=f'[Click Here]({ctx.message.jump_url})')

                try:
                    await webhook.send(embed=embed, username=f"{str(self.bot.user.display_name)} - Log",
                                       avatar_url=str(self.bot.user.avatar_url))
                except discord.HTTPException:
                    await webhook.send("Error, could not send embed.")
        except discord.Forbidden:
            pass


def setup(bot):
    bot.add_cog(Background(bot))
