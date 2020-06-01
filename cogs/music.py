import asyncio
import datetime
import itertools
import math
import random
import re
from typing import Union

import discord
import humanize
import wavelink
from discord.ext import commands
from wavelink import Equalizer

"""
Myst Open License - Version 0.1.
=====================================
Copyright (c) 2019 EvieePy(MysterialPy)

 This Source Code Form is subject to the terms of the Myst Open License, v. 0.1.
 If a copy of the MOL was not distributed with this file, You can obtain one at
 https://gist.github.com/EvieePy/bfe0332ad7bff98691f51686ded083ea.
"""
"""
The following code was based on the obtained code at 
https://github.com/PythonistaGuild/Wavelink/blob/master/examples/advanced/advanced.py
and has been modified to better suit our needs.
"""

RURL = re.compile(r'https?:\/\/(?:www\.)?.+')


class Track(wavelink.Track):
    __slots__ = ('requester', 'channel', 'message')

    def __init__(self, id_, info, *, ctx=None):
        super(Track, self).__init__(id_, info)

        self.requester = ctx.author
        self.channel = ctx.channel
        self.message = ctx.message

    @property
    def is_dead(self):
        return self.dead


class Player(wavelink.Player):

    def __init__(self, bot: Union[commands.Bot, commands.AutoShardedBot], guild_id: int, node: wavelink.Node):
        super(Player, self).__init__(bot, guild_id, node)

        self.queue = asyncio.Queue()
        self.next_event = asyncio.Event()

        self.volume = 40
        self.dj = None
        self.controller_message = None
        self.reaction_task = None
        self.update = False
        self.updating = False
        self.inactive = False

        self.controls = {'⏯': 'rp',
                         '⏹': 'stop',
                         '⏭': 'skip',
                         '🔀': 'shuffle',
                         '🔂': 'repeat',
                         '🔁': 'restart',
                         '🇶': 'queue',
                         '🔼': 'vol_up',
                         '🔽': 'vol_down'}

        self.pauses = set()
        self.resumes = set()
        self.stops = set()
        self.shuffles = set()
        self.skips = set()
        self.repeats = set()
        self.restarts = set()
        self.clears = set()

        self.eq = 'Flat'

        bot.loop.create_task(self.player_loop())
        bot.loop.create_task(self.updater())

    @property
    def entries(self):
        return list(self.queue._queue)

    async def updater(self):
        while not self.bot.is_closed():
            if self.update and not self.updating:
                self.update = False
                await self.invoke_controller()

            await asyncio.sleep(10)

    async def player_loop(self):
        await self.bot.wait_until_ready()

        await self.set_eq(Equalizer.flat())
        # We can do any pre loop prep here...
        await self.set_volume(self.volume)

        while True:
            self.next_event.clear()

            self.inactive = False

            song = await self.queue.get()
            if not song:
                continue

            self.current = song
            self.paused = False

            await self.play(song)

            # Invoke our controller if we aren't already...
            if not self.update:
                await self.invoke_controller()

            # Wait for TrackEnd event to set our event...
            await self.next_event.wait()

            # Clear votes...
            self.pauses.clear()
            self.resumes.clear()
            self.stops.clear()
            self.shuffles.clear()
            self.skips.clear()
            self.repeats.clear()
            self.restarts.clear()
            self.clears.clear()

    async def invoke_controller(self, track: wavelink.Track = None):
        """Invoke our controller message, and spawn a reaction controller if one isn't alive."""
        if not track:
            track = self.current

        self.updating = True

        embed = discord.Embed(title='Music Controller',
                              description=f'Now Playing:```ini\n{track.title}```\n\n',
                              color=0x1a74c7)
        embed.set_thumbnail(url=track.thumb)

        if track.is_stream:
            embed.add_field(name='Duration', value='🔴`Streaming`')
        else:
            embed.add_field(name='Duration', value=str(datetime.timedelta(milliseconds=int(track.length))))
        embed.add_field(name='Video URL', value=f'[Click Here]({track.uri})')
        embed.add_field(name='Requested By', value=track.requester.mention)
        embed.add_field(name='Current DJ', value=self.dj.mention)
        embed.add_field(name='Volume', value=f'**{self.volume}%**')
        embed.add_field(name='EQ', value=self.eq)
        # embed.add_field(name='Queue Length', value=str(len(self.entries)))

        if len(self.entries) > 0:
            data = '\n'.join(f'**-** `{t.title[0:45]}{"..." if len(t.title) > 45 else ""}`\n{"-" * 50}'
                             for t in itertools.islice([e for e in self.entries if not e.is_dead], 0, 3, None))
            embed.add_field(name=f'Queue ({str(len(self.entries))}): ', value=data, inline=False)

        if not await self.is_current_fresh(track.channel) and self.controller_message:
            try:
                await self.controller_message.delete()
            except discord.HTTPException:
                pass

            self.controller_message = await track.channel.send(embed=embed)
        elif not self.controller_message:
            self.controller_message = await track.channel.send(embed=embed)
        else:
            self.updating = False
            return await self.controller_message.edit(embed=embed, content=None)

        try:
            self.reaction_task.cancel()
        except Exception:
            pass

        self.reaction_task = self.bot.loop.create_task(self.reaction_controller())
        self.updating = False

    async def add_reactions(self):
        """Add reactions to our controller."""
        for reaction in self.controls:
            try:
                await self.controller_message.add_reaction(str(reaction))
            except discord.HTTPException:
                return

    async def reaction_controller(self):
        """
        Our reaction controller, attached to our controller.

        This handles the reaction buttons and it's controls.
        """
        self.bot.loop.create_task(self.add_reactions())

        def check(r, u):
            if not self.controller_message:
                return False
            elif str(r) not in self.controls.keys():
                return False
            elif u.id == self.bot.user.id or r.message.id != self.controller_message.id:
                return False
            elif u not in self.bot.get_channel(int(self.channel_id)).members:
                return False
            return True

        while self.controller_message:
            if self.channel_id is None:
                return self.reaction_task.cancel()

            react, user = await self.bot.wait_for('reaction_add', check=check)
            control = self.controls.get(str(react))

            if control == 'rp':
                if self.paused:
                    control = 'resume'
                else:
                    control = 'pause'

            try:
                await self.controller_message.remove_reaction(react, user)
            except discord.HTTPException:
                pass
            cmd = self.bot.get_command(control)

            ctx = await self.bot.get_context(react.message)
            ctx.author = user

            try:
                if cmd.is_on_cooldown(ctx):
                    pass
                if not await self.invoke_react(cmd, ctx):
                    pass
                else:
                    self.bot.loop.create_task(ctx.invoke(cmd))
            except Exception as e:
                ctx.command = self.bot.get_command('reactcontrol')
                await cmd.dispatch_error(ctx=ctx, error=e)

        await self.destroy_controller()

    async def destroy_controller(self):
        """Destroy both the main controller and it's reaction controller."""
        try:
            await self.controller_message.delete()
            self.controller_message = None
        except (AttributeError, discord.HTTPException):
            pass

        try:
            self.reaction_task.cancel()
        except Exception:
            pass

    async def invoke_react(self, cmd, ctx):
        if not cmd._buckets.valid:
            return True

        if not (await cmd.can_run(ctx)):
            return False

        bucket = cmd._buckets.get_bucket(ctx)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            return False
        return True

    async def is_current_fresh(self, chan):
        """Check whether our controller is fresh in message history."""
        try:
            async for m in chan.history(limit=8):
                if m.id == self.controller_message.id:
                    return True
        except (discord.HTTPException, AttributeError):
            return False
        return False


# noinspection PyUnresolvedReferences
class Music(commands.Cog):
    def __init__(self, bot: Union[commands.Bot, commands.AutoShardedBot]):
        self.bot = bot

        if not hasattr(bot, 'wavelink'):
            self.bot.wavelink = wavelink.Client(bot=bot)

        bot.loop.create_task(self.initiate_nodes())

    async def initiate_nodes(self):
        nodes = {
            'TidalWaveEast': {
                'host': '127.0.0.1',
                'port': 2333,
                'rest_url': 'http://127.0.0.1:2333',
                'password': "hvQe9As3VGGS",
                'identifier': 'TidalWaveEast',
                'region': 'us_east'
            }
        }

        for n in nodes.values():
            node = await self.bot.wavelink.initiate_node(host=n['host'],
                                                         port=n['port'],
                                                         rest_uri=n['rest_url'],
                                                         password=n['password'],
                                                         identifier=n['identifier'],
                                                         region=n['region'],
                                                         secure=False)

            node.set_hook(self.event_hook)

    def event_hook(self, event):
        """Our event hook. Dispatched when an event occurs on our Node."""
        if isinstance(event, wavelink.TrackEnd):
            event.player.next_event.set()
        elif isinstance(event, wavelink.TrackException):
            print(event.error)

    def required(self, player, invoked_with):
        """Calculate required votes."""
        channel = self.bot.get_channel(int(player.channel_id))
        if invoked_with == 'stop':
            if len(channel.members) - 1 == 2:
                return 2

        return math.ceil((len(channel.members) - 1) / 2.5)

    async def has_perms(self, ctx, **perms):
        """Check whether a member has the given permissions."""
        player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)

        if ctx.author.id == player.dj.id:
            return True

        ch = ctx.channel
        permissions = ch.permissions_for(ctx.author)

        missing = [perm for perm, value in perms.items() if getattr(permissions, perm, None) != value]

        if not missing:
            return True

        return False

    async def vote_check(self, ctx, command: str):
        player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)

        vcc = len(self.bot.get_channel(int(player.channel_id)).members) - 1
        votes = getattr(player, command + 's', None)

        if vcc < 3 and not ctx.invoked_with == 'stop':
            votes.clear()
            return True
        else:
            votes.add(ctx.author.id)

            if len(votes) >= self.required(player, ctx.invoked_with):
                votes.clear()
                return True
        return False

    async def do_vote(self, ctx, player, command: str):
        attr = getattr(player, command + 's', None)
        player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)

        if ctx.author.id in attr:
            await ctx.send(f'{ctx.author.mention}, you have already voted to {command}!', delete_after=15)
        elif await self.vote_check(ctx, command):
            await ctx.send(f'Vote request for {command} passed!', delete_after=20)
            to_do = getattr(self, f'do_{command}')
            await to_do(ctx)
        else:
            await ctx.send(f'{ctx.author.mention}, has voted to {command} the track!'
                           f' **{self.required(player, ctx.invoked_with) - len(attr)}** more votes needed!',
                           delete_after=30)

    async def delete_original(self, ctx):
        if not ctx.message.author.id == self.bot.user.id:
            try:
                await ctx.message.delete()
            except discord.HTTPException:
                pass

    @commands.command(name='reactcontrol', hidden=True)
    @commands.guild_only()
    async def react_control(self, ctx):
        """Dummy command for error handling in our player."""
        pass

    @commands.command(name='connect', aliases=['join'])
    @commands.guild_only()
    async def connect_(self, ctx, *, channel: discord.VoiceChannel = None):
        """Connect to voice."""
        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                raise discord.DiscordException('No channel to join. Please either specify a valid channel or join one.')

        player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)

        if player.is_connected:
            if ctx.author.voice.channel == ctx.guild.me.voice.channel:
                return

        await player.connect(channel.id)

    @commands.command(name='play', aliases=['sing'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.guild_only()
    async def play_(self, ctx, *, query: str):
        """
        Queue a track or playlist for playback.

        Query can be a search entry for YouTube, or a direct link to 
        SoundCloud, Bandcamp, Twitch, Mixer, Vimeo, or an HTTP source.
        """
        await ctx.trigger_typing()

        await ctx.invoke(self.connect_)
        query = query.strip('<>')
        # query, sep, tail = query.partition('&list=')
        query = query.partition('&list=')[0]

        player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)

        if not player.is_connected:
            return await ctx.send('Bot is not connected to voice. Please join a voice channel to play music.')

        if not player.dj:
            player.dj = ctx.author

        if not RURL.match(query):
            query = f'ytsearch:{query}'

        tracks = await self.bot.wavelink.get_tracks(query)
        if not tracks:
            return await ctx.send('No tracks were found with that query. Please try again.', delete_after=15)

        if isinstance(tracks, wavelink.TrackPlaylist):
            for t in tracks.tracks:
                await player.queue.put(Track(t.id, t.info, ctx=ctx))

            await ctx.send(f'Added the playlist `{tracks.data["playlistInfo"]["name"]}`'
                           f' with `{len(tracks.tracks)}` tracks to the queue.', delete_after=15)
        else:
            track = tracks[0]
            await ctx.send(f'Added `{track.title}` to the queue.', delete_after=15)
            await player.queue.put(Track(track.id, track.info, ctx=ctx))

        if player.controller_message and player.is_playing:
            await player.invoke_controller()

    @commands.command(name='now_playing', aliases=['np', 'current', 'currentrack', 'controller'])
    @commands.cooldown(2, 15, commands.BucketType.user)
    @commands.guild_only()
    async def now_playing(self, ctx):
        """Show the currently playing track and the music controller."""
        await self.delete_original(ctx)
        player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)
        if not player:
            return

        if not player.is_connected:
            return

        if player.updating or player.update:
            return

        await player.invoke_controller()

    @commands.command(name='pause')
    @commands.guild_only()
    async def pause_(self, ctx):
        """Pause the currently playing track."""
        await self.delete_original(ctx)
        player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)
        if not player:
            return

        if not player.is_connected:
            await ctx.send('I am not currently connected to voice!')

        if player.paused:
            return

        if await self.has_perms(ctx, manage_guild=True):
            await ctx.send(f'{ctx.author.mention} has paused the track.', delete_after=15)
            return await self.do_pause(ctx)

        await self.do_vote(ctx, player, 'pause')

    async def do_pause(self, ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)
        player.paused = True
        await player.set_pause(True)

    @commands.command(name='playnext', aliases=['bringfront'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.guild_only()
    async def play_next(self, ctx, *, title: str):
        """Pick a track from the queue to play next."""
        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass
        player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)

        if not player.is_connected:
            return await ctx.send('I am not currently connected to voice!')

        if not player.entries:
            return await ctx.send('No tracks in the queue!', delete_after=15)

        for track in player.entries:
            if title.lower() in track.title.lower():
                player.queue._queue.remove(track)
                player.queue._queue.appendleft(track)
                player.update = True
                return await ctx.send(f'Playing `{track.title}` next.', delete_after=15)

    @commands.command(name='remove', aliases=['rem'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.guild_only()
    async def remove_(self, ctx, *, title: str):
        """Pick a track from the queue to remove."""
        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass
        player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)

        if not player.is_connected:
            return await ctx.send('I am not currently connected to voice!')

        if not player.entries:
            return await ctx.send('No tracks in the queue!', delete_after=15)

        for track in player.entries:
            if title.lower() in track.title.lower():
                player.queue._queue.remove(track)
                player.update = True
                return await ctx.send(f'Removed `{track.title}` from the queue.', delete_after=15)

    @commands.command(name='resume')
    @commands.guild_only()
    async def resume_(self, ctx):
        """Resume a currently paused track."""
        await self.delete_original(ctx)
        player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)

        if not player.is_connected:
            await ctx.send('I am not currently connected to voice!')

        if not player.paused:
            return

        if await self.has_perms(ctx, manage_guild=True):
            await ctx.send(f'{ctx.author.mention} has resumed the track.', delete_after=15)
            return await self.do_resume(ctx)

        await self.do_vote(ctx, player, 'resume')

    async def do_resume(self, ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)
        await player.set_pause(False)

    @commands.command(name='seek')
    @commands.cooldown(5, 10, commands.BucketType.user)
    @commands.guild_only()
    async def seek_(self, ctx, time: int):
        """Seek to a time in the current track (in seconds)."""
        await self.delete_original(ctx)
        player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)

        if not player.is_connected:
            return await ctx.send('I am not currently connected to voice!')

        await player.seek(time * 1000)
        await ctx.send(f'Seeking to `{time}` seconds.', delete_after=15)

    # @commands.command(aliases=['ffd'])
    # @commands.cooldown(5, 10, commands.BucketType.user)
    # @commands.guild_only()
    # async def fast_forward(self, ctx, time: int):
    #     """Fast-Forward the track by a specified amount of seconds"""
    #     await self.delete_original(ctx)
    #     player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)
    #
    #     if not player.is_connected:
    #         return await ctx.send('I am not currently connected to voice!')
    #
    #     print(player.position)
    #
    #     # await player.seek(time*1000)
    #     # await ctx.send(f'Seeking to `{time}` seconds.', delete_after=15)

    @commands.command(name='skip')
    @commands.cooldown(5, 10, commands.BucketType.user)
    @commands.guild_only()
    async def skip_(self, ctx):
        """Skip the current track."""
        await self.delete_original(ctx)
        player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)

        if not player.is_connected:
            return await ctx.send('I am not currently connected to voice!')

        if await self.has_perms(ctx, manage_guild=True):
            await ctx.send(f'{ctx.author.mention} has skipped the track.', delete_after=15)
            return await self.do_skip(ctx)

        if player.current.requester.id == ctx.author.id:
            await ctx.send(f'The requester, {ctx.author.mention}, has skipped the track.')
            return await self.do_skip(ctx)

        await self.do_vote(ctx, player, 'skip')

    async def do_skip(self, ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)

        await player.stop()

    @commands.command(name='stop')
    @commands.cooldown(3, 30, commands.BucketType.guild)
    @commands.guild_only()
    async def stop_(self, ctx):
        """Stop the player, disconnect and clear the queue."""
        await self.delete_original(ctx)
        player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)

        if not player.is_connected:
            return await ctx.send('I am not currently connected to voice!')

        if await self.has_perms(ctx, manage_guild=True):
            await ctx.send(f'{ctx.author.mention} has stopped the player.', delete_after=15)
            return await self.do_stop(ctx)

        await self.do_vote(ctx, player, 'stop')

    async def do_stop(self, ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)
        player.queue._queue.clear()
        player.dj = None
        await player.stop()
        await player.disconnect()
        await player.destroy_controller()

    @commands.command(name='clear')
    @commands.cooldown(3, 30, commands.BucketType.guild)
    @commands.guild_only()
    async def clear_(self, ctx):
        """Clear the queue without stopping the bot."""
        await self.delete_original(ctx)
        player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)

        if not player.is_connected:
            return await ctx.send('I am not currently connected to voice!')

        if await self.has_perms(ctx, manage_guild=True):
            await ctx.send(f'{ctx.author.mention} has cleared the queue.', delete_after=15)
            return await self.do_clear(ctx)

        await self.do_vote(ctx, player, 'clear')

    async def do_clear(self, ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)
        player.queue._queue.clear()
        player.update = True

    @commands.command(name='volume', aliases=['vol'])
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.guild_only()
    async def volume_(self, ctx, *, value: int):
        """Change the player volume."""
        await self.delete_original(ctx)

        player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)

        if not player.is_connected:
            return await ctx.send('I am not currently connected to voice!')

        if not 0 < value < 101:
            return await ctx.send('Please enter a value between 1 and 100.')

        if not await self.has_perms(ctx, manage_guild=True) and player.dj.id != ctx.author.id:
            if (len(player.connected_channel.members) - 1) > 2:
                return

        await player.set_volume(value)
        await ctx.send(f'Set the volume to **{value}**%', delete_after=10)

        if not player.updating and not player.update:
            await player.invoke_controller()

    @commands.command(name='queue', aliases=['q', 'que'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def queue_(self, ctx):
        """Retrieve a list of currently queued tracks."""
        await self.delete_original(ctx)
        player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)

        if not player.is_connected:
            return await ctx.send('I am not currently connected to voice!')

        up_amt = 5
        upcoming = list(itertools.islice(player.entries, 0, up_amt))

        if not upcoming:
            return await ctx.send('No tracks in the queue!', delete_after=15)

        total_time = 0
        for track in player.entries:
            total_time += track.length

        embed = discord.Embed(
            title=f'Current Queue ({len(player.entries)}) [{str(datetime.timedelta(milliseconds=int(total_time)))}]',
            color=0x1a74c7)

        for track in upcoming:
            embed.add_field(name=f'({upcoming.index(track) + 1}) {track.title}',
                            value=f'{str(datetime.timedelta(milliseconds=int(track.length)))} - *Added by {track.requester.mention}*\n[Video URL]({track.uri})',
                            inline=False)

        amt_more = len(player.entries) - up_amt
        if amt_more > 0:
            embed.add_field(name='-', value=f'Plus {amt_more} more.')

        await ctx.send(embed=embed, delete_after=25)

    @commands.command(name='shuffle', aliases=['mix'])
    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.guild_only()
    async def shuffle_(self, ctx):
        """Shuffle the current queue."""
        await self.delete_original(ctx)
        player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)

        if not player.is_connected:
            return await ctx.send('I am not currently connected to voice!')

        if len(player.entries) < 3:
            return await ctx.send('Please add more tracks to the queue before trying to shuffle.', delete_after=10)

        if await self.has_perms(ctx, manage_guild=True):
            await ctx.send(f'{ctx.author.mention} has shuffled the queue.', delete_after=15)
            return await self.do_shuffle(ctx)

        await self.do_vote(ctx, player, 'shuffle')

    async def do_shuffle(self, ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)
        random.shuffle(player.queue._queue)

        player.update = True

    @commands.command(name='repeat')
    @commands.guild_only()
    async def repeat_(self, ctx):
        """Repeat the currently playing track."""
        await self.delete_original(ctx)
        player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)

        if not player.is_connected:
            return

        if await self.has_perms(ctx, manage_guild=True):
            await ctx.send(f'{ctx.author.mention} has repeated the track.', delete_after=10)
            return await self.do_repeat(ctx)

        await self.do_vote(ctx, player, 'repeat')

    async def do_repeat(self, ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)

        if not player.entries:
            await player.queue.put(player.current)
        else:
            player.queue._queue.appendleft(player.current)

        player.update = True

    @commands.command(name='restart')
    @commands.guild_only()
    async def restart_(self, ctx):
        """Restart the currently playing track."""
        await self.delete_original(ctx)
        player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)

        if not player.is_connected:
            return

        if await self.has_perms(ctx, manage_guild=True):
            await ctx.send(f'{ctx.author.mention} has restarted the track.', delete_after=10)
            return await self.do_restart(ctx)

        await self.do_vote(ctx, player, 'restart')

    async def do_restart(self, ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)

        if not player.entries:
            await player.queue.put(player.current)
        else:
            player.queue._queue.appendleft(player.current)

        await player.stop()

        # player.update = True

    @commands.command(name='vol_up', hidden=True)
    @commands.guild_only()
    async def volume_up(self, ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)

        if not player.is_connected:
            return

        vol = int(math.ceil((player.volume + 10) / 10)) * 10

        if vol > 100:
            vol = 100
            await ctx.send('Maximum volume reached', delete_after=7)

        await player.set_volume(vol)
        player.update = True

    @commands.command(name='vol_down', hidden=True)
    @commands.guild_only()
    async def volume_down(self, ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)

        if not player.is_connected:
            return

        vol = int(math.ceil((player.volume - 10) / 10)) * 10

        if vol < 0:
            vol = 0
            await ctx.send('Player is currently muted', delete_after=10)

        await player.set_volume(vol)
        player.update = True

    @commands.command(name='seteq', aliases=['eq', 'equalizer', 'setequalizer'])
    @commands.guild_only()
    async def set_eq(self, ctx, *, eq: str):
        """
        Set the equalizer.
        
        Types: flat (f) [default], boost (b), metal (m), piano (p)
        """

        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.message.delete()

        eq = eq.lower()
        eq_cls = Equalizer.flat()
        if eq in ["boost", "b"]:
            eq_cls = Equalizer.boost()
        elif eq in ["metal", "m"]:
            eq_cls = Equalizer.metal()
        elif eq in ["piano", "p"]:
            eq_cls = Equalizer.piano()

        player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)

        if eq.upper() not in player.equalizers:
            return await ctx.send(f'`{eq}` is not a valid equalizer!\nTry Flat, Boost, Metal, Piano.')

        await player.set_eq(eq_cls)
        player.eq = eq.capitalize()
        await ctx.send(f'The equalizer was set to `{eq.capitalize()}`', delete_after=15)
        player.update = True

    @commands.command(aliases=["controllerhelp", "chelp", "controlhelp"])
    async def controller_help(self, ctx):
        """Info on what each of the controller buttons mean"""

        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

        data = '⏯ - Pause/Resume\n' \
               '⏹ - Stop\n' \
               '⏭ - Skip\n' \
               '🔀 - Shuffle\n' \
               '🔂 - Repeat\n' \
               '🔁 - Restart\n' \
               '🇶 - Queue\n' \
               '🔼 - Volume Up\n' \
               '🔽 - Volume Down'
        await ctx.send(data, delete_after=15)

    @commands.command()
    @commands.guild_only()
    async def info(self, ctx):
        """Retrieve various Node/Server/Player information."""
        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

        player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player)
        node = player.node

        used = humanize.naturalsize(node.stats.memory_used)
        total = humanize.naturalsize(node.stats.memory_allocated)
        free = humanize.naturalsize(node.stats.memory_free)
        cpu = node.stats.cpu_cores

        fmt = f'**WaveLink:** `{wavelink.__version__}`\n\n' \
              f'Connected to `{len(self.bot.wavelink.nodes)}` nodes.\n' \
              f'Best available Node `{self.bot.wavelink.get_best_node().__repr__()}`\n' \
              f'`{len(self.bot.wavelink.players)}` player{"s are" if not len(self.bot.wavelink.players) == 1 else " is"} distributed on nodes.\n' \
              f'`{node.stats.players}` player{"s are" if not node.stats.players == 1 else " is"} distributed on server.\n' \
              f'`{node.stats.playing_players}` player{"s are" if not node.stats.playing_players == 1 else " is"} playing on server.\n\n' \
              f'Server Memory: `{used}/{total}` | `({free} free)`\n' \
              f'Server CPU: `{cpu}` cores\n\n' \
              f'Server Uptime: `{datetime.timedelta(milliseconds=node.stats.uptime)}`'
        await ctx.send(fmt)


def setup(bot):
    bot.add_cog(Music(bot))
