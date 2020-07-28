import copy
import io
import textwrap
import traceback
import typing
from contextlib import redirect_stdout

import discord
from discord.ext import commands

from util.checks import is_bot_owner
from util.data.guild_data import GuildData


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
        data = GuildData(str(ctx.guild.id))
        data.booleans.insert("test2", True)
        data.tags.insert("test2", "This is a test!")

        await ctx.send(data.booleans.fetch_by_name("rum"))


def setup(bot):
    bot.add_cog(Owner(bot))
