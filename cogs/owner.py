import copy
import typing

import discord
from discord.ext import commands

import util.userconf as uc
from util.checks import is_bot_owner

from util.data.guild_data import add


class GlobalChannel(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            return await commands.TextChannelConverter().convert(ctx, argument)
        except commands.BadArgument:
            # Not found... so fall back to ID + global lookup
            try:
                channel_id = int(argument, base=10)
            except ValueError:
                raise commands.BadArgument(f'Could not find a channel by ID {argument!r}.')
            else:
                channel = ctx.bot.get_channel(channel_id)
                if channel is None:
                    raise commands.BadArgument(f'Could not find a channel by ID {argument!r}.')
                return channel


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def botannounce(self, ctx, *, msg: str):
        """Announce too all users following the bot a message"""

        def check(m):
            return m.author.id == ctx.author.id

        msg_c = await ctx.send("Are you sure? Reply with **Yes** to confirm.")
        msg_wf = await self.bot.wait_for('message', check=check, timeout=15)

        if msg_wf.content == "Yes":
            embed = discord.Embed(title="Announcement", color=0xffffff)
            embed.description = f'{msg}\n\n\nYou received this message because you\'re subscribed as follower. Do `{ctx.prefix}follow` to unsubscribe.'
            embed.set_footer(text=f'Sent by {ctx.author.name}#{ctx.author.discriminator}')

            users = uc.get_all_if_equals("follow_mode", True)
            sent = False
            for u in users:
                user = self.bot.get_user(int(u))
                if user:
                    await user.send(embed=embed)
                    sent = True
            if sent:
                await ctx.send(f'Message sent!\n```{msg}```')
            else:
                await ctx.send(f'Message wasn\'t sent.')
        else:
            await msg_c.delete()
            await ctx.send("Aborted!")

    @commands.command()
    @commands.is_owner()
    async def changepresence(self, ctx, *, presence: str):
        """Change the bot's presence on the fly"""
        await self.bot.change_presence(activity=discord.Activity(name=presence, type=discord.ActivityType.playing))
        await ctx.send(f"Changed presence to `{presence}`")

    @commands.command()
    @commands.is_owner()
    async def getservers(self, ctx):
        """Get a a list of all servers the bot is currently connected to"""
        max_chars = 1750
        guilds = '\n'.join(f"{guild.name} ({guild.id})" for guild in self.bot.guilds)
        guild_parts = [(guilds[i:i + max_chars]) for i in range(0, len(guilds), max_chars)]

        for part in guild_parts:
            await ctx.author.send(f"```{part}```")
        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.send('Check your DMs!')

    @commands.command()
    @commands.is_owner()
    async def leaveserver(self, ctx, id: int):
        """Make the bot leave a server"""
        guild = self.bot.get_guild(id)
        await guild.leave()
        await ctx.send(f'Left **{guild.name}** (*{guild.id}*).')

    # @commands.command(hidden=True, aliases=["reload"])
    # @commands.is_owner()
    # async def restartbot(self, ctx):
    #     await ctx.send("Restarting bot...")
    #     print(f'Restarting bot...')
    #     await self.bot.logout()
    #     self.bot.run(self.bot.bot_token)

    # noinspection PyBroadException
    @commands.command(name="reloadmusic")
    @is_bot_owner()
    async def reload_music(self, ctx):
        """Reload the music module"""
        await ctx.send("Reloading music...")
        try:
            self.bot.reload_extension("cogs.music")
            await ctx.send("Music reloaded.")
        except Exception as e:
            print(e)
            await ctx.send("Error reloading!")

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx):
        """Shut the bot down."""
        await ctx.send("Shutting down bot...")
        await self.bot.logout()

    @commands.command()
    @commands.is_owner()
    async def sudo(self, ctx, channel: typing.Optional[GlobalChannel], who: discord.User, *, command: str):
        """Run a command as another user, optionally in another channel."""
        msg = copy.copy(ctx.message)
        channel = channel or ctx.channel
        msg.channel = channel
        msg.author = channel.guild.get_member(who.id) or who
        msg.content = ctx.prefix + command
        new_ctx = await self.bot.get_context(msg, cls=type(ctx))
        await self.bot.invoke(new_ctx)

    @commands.command()
    @commands.is_owner()
    async def test(self, ctx):
        """TEST COMMAND"""
        add()


def setup(bot):
    bot.add_cog(Owner(bot))
