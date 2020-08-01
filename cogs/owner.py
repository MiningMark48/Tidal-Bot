import asyncio
import copy
import io
import textwrap
import time
import traceback
import typing
from contextlib import redirect_stdout

import discord
from discord.ext import commands

from util.checks import is_bot_owner
from util.data.guild_data import GuildData
from util.logger import Logger


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


class PerformanceMocker:
    """A mock object that can also be used in await expressions."""

    def __init__(self):
        self.loop = asyncio.get_event_loop()

    # pylint: disable=assigning-non-slot
    @staticmethod
    def permissions_for(obj):
        # Lie and say we don't have permissions to embed
        # This makes it so pagination sessions just abruptly end on __init__
        # Most checks based on permission have a bypass for the owner anyway
        # So this lie will not affect the actual command invocation.
        perms = discord.Permissions.all()
        perms.administrator = False
        perms.embed_links = False
        perms.add_reactions = False
        return perms

    def __getattr__(self, attr):
        return self

    def __call__(self, *args, **kwargs):
        return self

    def __repr__(self):
        return '<PerformanceMocker>'

    def __await__(self):
        future = self.loop.create_future()
        future.set_result(self)
        return future.__await__()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return self

    def __len__(self):
        return 0

    def __bool__(self):
        return False


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self._last_result = None

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    @commands.command()
    @commands.is_owner()
    async def changepresence(self, ctx, *, presence: str):
        """Change the bot's presence on the fly"""
        await self.bot.change_presence(activity=discord.Activity(name=presence, type=discord.ActivityType.playing))
        await ctx.send(f"Changed presence to `{presence}`")
        Logger.info(f"{ctx.author} changed presence to {presence}")

    # noinspection PyBroadException
    @commands.command(aliases=["pyeval"])
    @commands.is_owner()
    async def eval(self, ctx, *, body: str):
        """Evaluates code"""

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except Exception:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')

        Logger.info(f"{ctx.author} evaluated Python")

    @commands.command()
    @commands.is_owner()
    async def getservers(self, ctx):
        """Get a list of all servers the bot is currently connected to"""
        max_chars = 1750
        guilds = '\n'.join(f"{guild.name} ({guild.id})" for guild in self.bot.guilds)
        guild_parts = [(guilds[i:i + max_chars]) for i in range(0, len(guilds), max_chars)]

        for part in guild_parts:
            await ctx.author.send(f"```{part}```")
        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.send('Check your DMs!')

        Logger.info(f"{ctx.author} received list of servers")

    @commands.command()
    @commands.is_owner()
    async def leaveserver(self, ctx, id: int):
        """Make the bot leave a server"""
        guild = self.bot.get_guild(id)
        await guild.leave()
        await ctx.send(f'Left **{guild.name}** (*{guild.id}*).')

        Logger.info(f"{ctx.author} made bot leave {guild.name}:{guild.id}")

    @commands.command()
    @commands.is_owner()
    async def perf(self, ctx, *, command):
        """Checks the timing of a command, attempting to suppress HTTP and DB calls."""

        msg = copy.copy(ctx.message)
        msg.content = ctx.prefix + command

        new_ctx = await self.bot.get_context(msg, cls=type(ctx))
        new_ctx._db = PerformanceMocker()

        # Intercepts the Messageable interface a bit
        new_ctx._state = PerformanceMocker()
        new_ctx.channel = PerformanceMocker()

        if new_ctx.command is None:
            return await ctx.send('No command found')

        start = time.perf_counter()
        try:
            await new_ctx.command.invoke(new_ctx)
        except commands.CommandError:
            end = time.perf_counter()
            success = False
            try:
                await ctx.send(f'```py\n{traceback.format_exc()}\n```')
            except discord.HTTPException:
                pass
        else:
            end = time.perf_counter()
            success = True

        await ctx.send(f'Status: {"Success" if success else "Fail"}\nTime: {(end - start) * 1000:.2f}ms')

        Logger.info(f"{ctx.author} checked performance of {command}")

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

        Logger.info(f"{ctx.author} reloaded music")

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx):
        """Shut the bot down."""
        await ctx.send("Shutting down bot...")

        Logger.info(f"{ctx.author} shutdown the bot")

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

        Logger.info(f"{ctx.author} did sudo: {command} to {who}")

    @commands.command()
    @commands.is_owner()
    async def test(self, ctx):
        """TEST COMMAND"""
        data = GuildData(str(ctx.guild.id))
        data.booleans.insert("test2", True)
        data.tags.insert("test2", "This is a test!")

        await ctx.send(data.booleans.fetch_by_name("rum"))

        Logger.info(f"{ctx.author} TEST COMMAND")


def setup(bot):
    bot.add_cog(Owner(bot))
