import time

import discord
from discord.ext import commands

import util.userconf as uc

start_time = time.time()


class Bot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def feedback(self, ctx, *, content: str):
        """
        Gives feedback about the bot.
        This is a quick way to request features and submit issues.
        The bot will communicate with you via DM about the status of your request if possible and when able.
        """

        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.message.delete()

        embed = discord.Embed(title='Feedback', colour=0x6777EC)
        channel = self.bot.get_channel(705639785238102036)  # TODO: Make config
        if channel is None:
            return

        embed.set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url)
        embed.description = content
        embed.timestamp = ctx.message.created_at

        if ctx.guild is not None:
            embed.add_field(name='Server', value=f'{ctx.guild.name}\n{ctx.guild.id}', inline=False)

        embed.add_field(name='Channel', value=f'{ctx.channel}\n{ctx.channel.id}', inline=False)
        embed.set_footer(text=f'Author ID: {ctx.author.id}')

        msg = await channel.send(embed=embed)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")

        await ctx.send(f'Successfully sent feedback.')

    # noinspection PyBroadException
    @commands.command(name="feedbackdm", aliases=["fbdm"])
    @commands.is_owner()
    async def feedback_dm(self, ctx, user_id: int, *, content: str):
        user = self.bot.get_user(user_id)

        embed = discord.Embed(title='Feedback', colour=0x6777EC)
        embed.add_field(name="Message", value=content)
        embed.description = '*This is DM was sent because you had previously submitted feedback.' \
                            'This DM is not monitored as is used to provide an update of your request.*'
        try:
            await user.send(embed=embed)
        except Exception:
            await ctx.send(f'Could not DM user by the ID: `{user_id}`')
        else:
            await ctx.send('DM successfully sent.')

    @commands.command(aliases=["botfollow", "followmode"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def follow(self, ctx):
        """
        Receive bot updates.

        When following, you will receive DMs from the bot regarding
        information on bot updates, when the bot is going offline, etc.
        """

        result = not uc.get_v(str(ctx.author.id), "follow_mode")
        if result is None:
            result = True
        uc.set_kv(str(ctx.author.id), "follow_mode", bool(result))

        await ctx.send(f'{ctx.author.mention}, you are {"now" if result else "no longer"} in follow mode.')


def setup(bot):
    bot.add_cog(Bot(bot))
