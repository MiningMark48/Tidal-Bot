import asyncio
import datetime
import re
import typing
import itertools
import humanize
import random
import copy
from typing import Union, Optional

import wavelink
from wavelink import Equalizer
import discord
from discord.ext import commands

from util.data.user_data import UserData
from util.config import BotConfig
from util.decorators import delete_original


RURL = re.compile(r'https?:\/\/(?:www\.)?.+')


class MusicEmbed:
    def __init__(self, content: str, user: discord.member = None):
        self.embed = discord.Embed(title="Music", color=0x6fc3f3)
        self.embed.description = content
        if user:
            self.embed.set_footer(text=f"{user.name}")

    def get(self):
        return self.embed


class MusicController:
    def __init__(self, bot, guild_id):
        self.bot = bot
        self.guild_id = guild_id
        self.channel = None

        self.next = asyncio.Event()
        self.queue = asyncio.Queue()

        self.volume = 40
        self.now_playing = None

        self.bot.loop.create_task(self.controller_loop())

    async def controller_loop(self):
        await self.bot.wait_until_ready()

        player = self.bot.wavelink.get_player(self.guild_id)
        await player.set_volume(self.volume)

        while True:
            if self.now_playing:
                await self.now_playing.delete()

            self.next.clear()

            print(len(self.queue._queue))   

            song = await self.queue.get()
            await player.play(song)
            # self.now_playing = await self.channel.send(embed=MusicEmbed(f"**Now playing:**\n`{song}`").get())
            self.now_playing = await self.channel.send(embed=MusicEmbed(f"**Now playing:**\n`[{get_duration(song)}]\t{song}`").get())

            await self.next.wait()


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.controllers = {}

        self.config = BotConfig().load_data()

        if not hasattr(bot, 'wavelink'):
            self.bot.wavelink = wavelink.Client(bot=self.bot)

        self.bot.loop.create_task(self.start_nodes())

    async def start_nodes(self):
        await self.bot.wait_until_ready()

        nodes = self.config["music"]["nodes"]

        for n in nodes.values():
            node = await self.bot.wavelink.initiate_node(host=n['host'],
                                                         port=n['port'],
                                                         rest_uri=n['rest_url'],
                                                         password=n['password'],
                                                         identifier=n['identifier'],
                                                         region=n['region'],
                                                         secure=False)
            node.set_hook(self.on_event_hook)

    async def on_event_hook(self, event):
        """Node callback"""
        if isinstance(event, (wavelink.TrackEnd, wavelink.TrackException)):
            controller = self.get_controller(event.player)
            controller.next.set()

    def get_controller(self, value: Union[commands.Context, wavelink.Player]):
        if isinstance(value, commands.Context):
            gid = value.guild.id
        else:
            gid = value.guild_id

        try:
            controller = self.controllers[gid]
        except KeyError:
            controller = MusicController(self.bot, gid)
            self.controllers[gid] = controller

        return controller

    async def cog_check(self, ctx):
        """Local check"""
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def cog_command_error(self, ctx, error):
        """Local error handler"""
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send("This command can't be used in a DM!")
            except discord.HTTPException:
                pass

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @delete_original()
    async def connect(self, ctx, *, channel: discord.VoiceChannel = None):
        """Connect to a voice channel"""

        if ctx.guild.id not in self.config["music"]["whitelist_servers"]:
            return await ctx.send(embed=MusicEmbed("Server not whitelisted for music! Bot won't connect.", ctx.author).get(), delete_after=15)

        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                raise discord.DiscordException(
                    "Can't join. Please specify a channel or join one!")

        player = self.bot.wavelink.get_player(ctx.guild.id)
        await ctx.send(embed=MusicEmbed(f"Connecting to **`{channel.name}`**...", ctx.author).get(), delete_after=15)
        await player.connect(channel.id)

        controller = self.get_controller(ctx)
        controller.channel = ctx.channel

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @delete_original()
    async def play(self, ctx, *, query: str):
        """Search for a song and add it to the queue"""

        query = query.strip('<>')
        query = query.partition('&list=')[0]

        if not RURL.match(query):
            query = f"ytsearch:{query}"

        tracks = await self.bot.wavelink.get_tracks(query)

        if not tracks:
            return await ctx.send(embed=MusicEmbed(f"**Could not find any songs!`**", ctx.author).get(), delete_after=15)

        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_connected:
            await ctx.invoke(self.connect)

        controller = self.get_controller(ctx)
        if isinstance(tracks, wavelink.TrackPlaylist):
            for t in tracks.tracks:
                await controller.queue.put(t)

            await ctx.send(embed=MusicEmbed(f'Added the playlist `{tracks.data["playlistInfo"]["name"]}`'
                                            f' with `{len(tracks.tracks)}` tracks to the queue.', ctx.author).get(), delete_after=15)
        else:
            track = tracks[0]
            await ctx.send(embed=MusicEmbed(f"Added `{str(track)}` to the queue", ctx.author).get(), delete_after=15)
            await controller.queue.put(track)

        # track = tracks[0]
        # controller = self.get_controller(ctx)
        # await controller.queue.put(track)
        # await ctx.send(embed=MusicEmbed(f"Added `{str(track)}` to the queue", ctx.author).get(), delete_after=15)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @delete_original()
    async def pause(self, ctx):
        """Pause the player"""

        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send(embed=MusicEmbed("I am not playing anything!", ctx.author).get(), delete_after=15)

        await ctx.send(embed=MusicEmbed("Pausing the song!", ctx.author).get(), delete_after=15)
        await player.set_pause(True)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @delete_original()
    async def resume(self, ctx):
        """Resume the player"""

        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.paused:
            return await ctx.send(embed=MusicEmbed("I am not paused!", ctx.author).get(), delete_after=15)

        await ctx.send(embed=MusicEmbed("Resuming the player!", ctx.author).get(), delete_after=15)
        await player.set_pause(False)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @delete_original()
    async def skip(self, ctx):
        """Skip the currently playing song."""

        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send(embed=MusicEmbed("I am not playing anything!", ctx.author).get(), delete_after=15)

        await ctx.send(embed=MusicEmbed("Skipping the song!", ctx.author).get(), delete_after=15)
        await player.stop()

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @delete_original()
    async def volume(self, ctx, *, vol: int):
        """Set the player volume"""

        player = self.bot.wavelink.get_player(ctx.guild.id)
        controller = self.get_controller(ctx)

        vol = max(min(vol, 1000), 0)
        controller.volume = vol

        await ctx.send(embed=MusicEmbed(f"Setting the plater volume to `{vol}`", ctx.author).get(), delete_after=15)
        await player.set_volume(vol)

    @commands.command(name="nowplaying", aliases=["np"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    @delete_original()
    async def now_playing(self, ctx):
        """Get the currently playing song"""

        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.current:
            return await ctx.send(embed=MusicEmbed("I am not playing anything!", ctx.author).get(), delete_after=15)

        controller = self.get_controller(ctx)
        if controller.now_playing:
            await controller.now_playing.delete()

        current_track = player.current
        controller.now_playing = await ctx.send(embed=MusicEmbed(f"**Now playing:**\n`[{get_duration(current_track)}]\t{current_track}`").get())

    @commands.command(aliases=["q"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    @delete_original()
    async def queue(self, ctx):
        """Get the current player queue"""

        player = self.bot.wavelink.get_player(ctx.guild.id)
        controller = self.get_controller(ctx)

        if not player.current or not controller.queue._queue:
            return await ctx.send(embed=MusicEmbed("There are no songs in the queue!").get(), delete_after=15)

        slice_size = 5
        queue = controller.queue._queue
        upcoming = list(itertools.islice(queue, 0, slice_size))

        total_time = 0
        for track in queue:
            total_time += track.length

        header = f'**Current Queue** ({len(queue)}) [{str(datetime.timedelta(milliseconds=int(total_time)))}]'
        fmt = '\n'.join(f'** `▶ [{get_duration(song)}] {str(song)}`**\n' for song in upcoming)        
        embed = MusicEmbed(f"{header}\n{fmt}").get()
        if len(queue) > slice_size:
            embed.set_footer(text=f"Plus {str(len(queue) - slice_size)} more.")

        await ctx.send(embed=embed, delete_after=15)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @delete_original()
    async def stop(self, ctx):
        """Stop and disconnect the player and controller"""

        player = self.bot.wavelink.get_player(ctx.guild.id)

        try:
            del self.controllers[ctx.guild.id]
        except KeyError:
            await player.disconnect()
            return await ctx.send(embed=MusicEmbed("There was no controller to stop", ctx.author).get(), delete_after=15)

        await player.disconnect()
        await ctx.send(embed=MusicEmbed("Disconnected player and killed controller.", ctx.author).get(), delete_after=15)

    @commands.command(name='playnext', aliases=['bringfront'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    @delete_original()
    async def play_next(self, ctx, *, title: str):
        """Pick a track from the queue to play next."""

        player = self.bot.wavelink.get_player(ctx.guild.id)

        if not player.is_connected:
            return await ctx.send(embed=MusicEmbed("I am not connected to voice!", ctx.author).get(), delete_after=15)

        queue = self.get_controller(ctx).queue._queue
        if not player.current or not queue:
            return await ctx.send(embed=MusicEmbed("There are no songs in the queue!", ctx.author).get(), delete_after=15)

        for track in queue:
            if title.lower() in track.title.lower():
                queue.remove(track)
                queue.appendleft(track)
                return await ctx.send(embed=MusicEmbed(f"Playing `{track.title}` next.", ctx.author).get(), delete_after=15)

    @commands.command(aliases=['rem'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    @delete_original()
    async def remove(self, ctx, *, title: str):
        """Pick a track from the queue to remove."""

        player = self.bot.wavelink.get_player(ctx.guild.id)

        if not player.is_connected:
            return await ctx.send(embed=MusicEmbed("I am not connected to voice!", ctx.author).get(), delete_after=15)

        queue = self.get_controller(ctx).queue._queue
        if not queue:
            return await ctx.send(embed=MusicEmbed("There are no songs in the queue!", ctx.author).get(), delete_after=15)

        for track in queue:
            if title.lower() in track.title.lower():
                queue.remove(track)
                return await ctx.send(embed=MusicEmbed(f"Removed `{track.title}` from the queue.", ctx.author).get(), delete_after=15)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @delete_original()
    async def clear(self, ctx):
        """Clear the queue"""

        player = self.bot.wavelink.get_player(ctx.guild.id)

        if not player.is_connected:
            return await ctx.send(embed=MusicEmbed("I am not connected to voice!", ctx.author).get(), delete_after=15)

        queue = self.get_controller(ctx).queue._queue
        if not queue:
            return await ctx.send(embed=MusicEmbed("There are no songs in the queue!", ctx.author).get(), delete_after=15)

        queue.clear()
        await ctx.send(embed=MusicEmbed("Cleared the queue.", ctx.author).get(), delete_after=15)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @delete_original()
    async def shuffle(self, ctx):
        """Shuffle the queue"""

        player = self.bot.wavelink.get_player(ctx.guild.id)

        if not player.is_connected:
            return await ctx.send(embed=MusicEmbed("I am not connected to voice!", ctx.author).get(), delete_after=15)

        queue = self.get_controller(ctx).queue._queue
        if not queue:
            return await ctx.send(embed=MusicEmbed("There are no songs in the queue!", ctx.author).get(), delete_after=15)

        random.shuffle(queue)
        await ctx.send(embed=MusicEmbed("Shuffled the queue.", ctx.author).get(), delete_after=15)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @delete_original()
    async def repeat(self, ctx):
        """Repeat a song"""

        player = self.bot.wavelink.get_player(ctx.guild.id)

        if not player.is_connected:
            return await ctx.send(embed=MusicEmbed("I am not connected to voice!", ctx.author).get(), delete_after=15)

        queue = self.get_controller(ctx).queue._queue
        if not queue:
            queue.append(player.current)
        else:
            queue.appendleft(player.current)

        await ctx.send(embed=MusicEmbed("Repeated the song.", ctx.author).get(), delete_after=15)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @delete_original()
    async def restart(self, ctx):
        """Restart a song"""

        player = self.bot.wavelink.get_player(ctx.guild.id)

        if not player.is_connected:
            return await ctx.send(embed=MusicEmbed("I am not connected to voice!", ctx.author).get(), delete_after=15)

        queue = self.get_controller(ctx).queue._queue
        if not queue:
            queue.append(player.current)
        else:
            queue.appendleft(player.current)
        await player.stop()

        await ctx.send(embed=MusicEmbed("Restarted the song.", ctx.author).get(), delete_after=15)

    @commands.command()
    @commands.cooldown(5, 10, commands.BucketType.user)
    @delete_original()
    async def seek(self, ctx, time: int):
        """Seek to a time in the current track (in seconds)."""

        player = self.bot.wavelink.get_player(ctx.guild.id)

        if not player.is_connected:
            return await ctx.send(embed=MusicEmbed("I am not connected to voice!", ctx.author).get(), delete_after=15)

        await player.seek(time * 1000)
        await ctx.send(embed=MusicEmbed(f"Seeking to `{time}` seconds.", ctx.author).get(), delete_after=15)

    # @commands.command(name='seteq', aliases=['eq', 'equalizer', 'setequalizer'])
    # @commands.cooldown(5, 10, commands.BucketType.user)
    # @delete_original()
    # async def set_eq(self, ctx, *, eq: str):
    #     """
    #     Set the equalizer.

    #     Types: flat (f) [default], boost (b), metal (m), piano (p)
    #     """

    #     eq = eq.lower()
    #     # eq_cls = Equalizer.flat()
    #     if eq in ["boost", "b"]:
    #         eq_cls = Equalizer.boost()
    #     elif eq in ["metal", "m"]:
    #         eq_cls = Equalizer.metal()
    #     elif eq in ["piano", "p"]:
    #         eq_cls = Equalizer.piano()
    #     else:
    #         return await ctx.send(f'`{eq}` is not a valid equalizer!\nTry Flat, Boost, Metal, Piano.')

    #     player = self.bot.wavelink.get_player(ctx.guild.id)

    #     await player.set_eq(eq_cls)
    #     player.eq = eq.capitalize()
    #     await ctx.send(embed=MusicEmbed(f"The equalizer was set to `{eq.capitalize()}`", ctx.author).get(), delete_after=15)

    @commands.command(name="setplaylist", aliases=["addplaylist"])
    @commands.cooldown(1, 2)
    @delete_original()
    async def set_playlist(self, ctx, playlist_name: str, *, youtube_url: str):
        """Save a link to a YouTube playlist."""

        if not youtube_url.startswith("https://www.youtube.com/playlist?list="):
            await ctx.send("Invalid playlist!")
            return

        UserData(str(ctx.author.id)).playlists.set(playlist_name, youtube_url)

        await ctx.send(embed=MusicEmbed(f"**Saved** <{youtube_url}> as *{playlist_name}*.", ctx.author).get(), delete_after=15)

    @commands.command(name="removeplaylist", aliases=["remplaylist", "delplaylist"])
    @commands.cooldown(1, 2)
    @delete_original()
    async def remove_playlist(self, ctx, playlist_name: str):
        """Remove a saved YouTube playlist."""

        if not UserData(str(ctx.author.id)).playlists.fetch_by_name(playlist_name):
            await ctx.send("Playlist not found.")
            return

        UserData(str(ctx.author.id)).playlists.delete(playlist_name)

        await ctx.send(embed=MusicEmbed(f"**Removed** the playlist *{playlist_name}*.", ctx.author).get(), delete_after=15)

    @commands.command(name="playplaylist", aliases=["getplaylist"])
    @commands.cooldown(1, 5)
    @delete_original()
    async def play_playlist(self, ctx, playlist_name: str):
        """Play a previously saved YouTube playlist."""

        playlist = UserData(
            str(ctx.author.id)).playlists.fetch_by_name(playlist_name)

        if not playlist:
            return await ctx.send(embed=MusicEmbed("Playlist not found.", ctx.author).get(), delete_after=15)

        msg = copy.copy(ctx.message)
        msg.content = f"{ctx.prefix}play {playlist}"
        new_ctx = await self.bot.get_context(msg, cls=type(ctx))
        await self.bot.invoke(new_ctx)

    @commands.command(name="listplaylists", aliases=["getplaylists", "showplaylists", "playlists"])
    @commands.cooldown(1, 10)
    @delete_original()
    async def list_playlists(self, ctx):
        """Show all available YouTube playlists."""

        playlists_o = sorted([(_pl[1], _pl[2]) for _pl in list(
            UserData(str(ctx.author.id)).playlists.fetch_all())])

        if len(playlists_o) == 0:
            return await ctx.send(embed=MusicEmbed("No playlists found!", ctx.author).get(), delete_after=15)

        playlists_o.insert(0, ("Name", "URL\n"))

        pl_names = [i[0] for i in playlists_o]

        max_chars = 1750
        playlists = '\n'.join(
            f"{str(pl[0]).ljust(len(max(pl_names, key=len)) + 3, ' ')} {pl[1]}" for pl in playlists_o)
        playlist_parts = [(playlists[i:i + max_chars])
                          for i in range(0, len(playlists), max_chars)]

        for part in playlist_parts:
            await ctx.send(f"```{part}```")
            # await ctx.send(embed=MusicEmbed(f"```{part}```", ctx.author).get(), delete_after=15)

    @commands.command(name="musicinfo", hidden=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    @delete_original()
    async def music_info(self, ctx):
        """Retrieve various Node/Server/Player information."""

        player = self.bot.wavelink.get_player(ctx.guild.id)
        node = player.node

        used = humanize.naturalsize(node.stats.memory_used)
        total = humanize.naturalsize(node.stats.memory_allocated)
        free = humanize.naturalsize(node.stats.memory_free)
        cpu = node.stats.cpu_cores

        fmt = f'**WaveLink:** `{wavelink.__version__}`\n\n' \
              f'Connected to `{len(self.bot.wavelink.nodes)}` nodes.\n' \
              f'Best available Node `{self.bot.wavelink.get_best_node().__repr__()}`\n' \
              f'`{len(self.bot.wavelink.players)}` players are distributed on nodes.\n' \
              f'`{node.stats.players}` players are distributed on server.\n' \
              f'`{node.stats.playing_players}` players are playing on server.\n\n' \
              f'Server Memory: `{used}/{total}` | `({free} free)`\n' \
              f'Server CPU: `{cpu}`\n\n' \
              f'Server Uptime: `{datetime.timedelta(milliseconds=node.stats.uptime)}`'
        await ctx.send(fmt)


def get_duration(track):
    duration = "\N{LARGE RED CIRCLE}" if track.is_stream else str(
        datetime.timedelta(milliseconds=int(track.length)))
    return duration

def setup(bot):
    bot.add_cog(Music(bot))
