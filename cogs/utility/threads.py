import copy
import typing

import discord
from discord.ext import commands

from util.decorators import delete_original
from util.messages import MessagesUtil


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.messages_util = MessagesUtil(bot)
        self.threads_cat_name = "Threads"
        self.thread_emoji = "\N{Spool of Thread}"

    async def thread_start(self, ctx, msg_id: typing.Optional[str]):
        cat_thread = discord.utils.get(ctx.guild.categories, name=self.threads_cat_name)
        if cat_thread is None:
            cat_thread = await ctx.guild.create_category(name=self.threads_cat_name)

        if msg_id:
            try:
                thread_msg = await ctx.channel.fetch_message(msg_id)
            except discord.errors.NotFound:
                return await ctx.send("Channel not found!")
        else:
            try:
                msgs = await ctx.channel.history(limit=1).flatten()
                thread_msg = msgs[0]
            except IndexError:
                thread_msg = ctx.message

        overwrites = ctx.channel.overwrites
        thread_channel = await ctx.guild.create_text_channel(name=thread_msg.id,
                                                             category=cat_thread,
                                                             overwrites=overwrites,
                                                             topic=f"Author: {ctx.author.id}",
                                                             reason="Start Thread")

        embed = discord.Embed(title="Threaded Message")
        embed.set_author(name=thread_msg.author.display_name, icon_url=thread_msg.author.avatar_url)
        embed.description = thread_msg.content
        thread_msg_embed = await thread_channel.send(embed=embed)
        await thread_msg_embed.pin()

        embed.title = "Thread Created"
        embed.description = f"{thread_channel.mention}\n\n{embed.description}"
        await ctx.send(embed=embed)

    @commands.group(aliases=["threads"])
    async def thread(self, ctx):
        """
        Channel Threads, until added officially by Discord

        (Threads can also be started by reacting with the thread emoji)

        Note: This is experimental, use with caution!
        """

        if ctx.invoked_subcommand is None:
            await ctx.send(f"Invalid subcommand! ")

            msg = copy.copy(ctx.message)
            msg.content = f"{ctx.prefix}help {ctx.command}"
            new_ctx = await self.bot.get_context(msg, cls=type(ctx))
            await self.bot.invoke(new_ctx)

    @thread.command(aliases=["begin"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    @delete_original()
    async def start(self, ctx, msg_id: typing.Optional[str]):
        """
        Start a thread based on the last sent message or a message ID.
        """

        await self.thread_start(ctx, msg_id)

    @thread.command(aliases=["stop"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    @delete_original()
    async def end(self, ctx):
        """
        End a thread.
        """

        async def delete():
            await ctx.channel.delete(reason="End Thread")

        if ctx.channel.category:
            if not ctx.channel.category.name == self.threads_cat_name:
                return await ctx.send("This is not a thread!")

        can_delete = False
        if ctx.channel.permissions_for(ctx.author).manage_channels:
            await delete()
            return

        if not can_delete:
            if ctx.channel.topic:
                topic = ctx.channel.topic.replace("Author: ", "")
                if topic == str(ctx.author.id):
                    await delete()
                    return
                else:
                    return await ctx.send("Unable to find author id!")
            else:
                return await ctx.send("Unable to find author id!")

        await ctx.send("You don't have permission!")

    @thread.command(aliases=["edit"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    @delete_original()
    async def rename(self, ctx, name: str):
        """
        Rename a thread.
        """

        async def rename():
            # await ctx.channel.delete(reason="End Thread")
            await ctx.channel.edit(name=f"thread-{name}")
            await ctx.send(f"Renamed thread channel to `thread-{name}`.", delete_after=10)
            pass

        if ctx.channel.category:
            if not ctx.channel.category.name == self.threads_cat_name:
                return await ctx.send("This is not a thread!")

        can_delete = False
        if ctx.channel.permissions_for(ctx.author).manage_channels:
            await rename()
            return

        if not can_delete:
            if ctx.channel.topic:
                topic = ctx.channel.topic.replace("Author: ", "")
                if topic == str(ctx.author.id):
                    await rename()
                    return
                else:
                    return await ctx.send("Unable to find author id!")
            else:
                return await ctx.send("Unable to find author id!")

        await ctx.send("You don't have permission!")

    @commands.Cog.listener("on_raw_reaction_add")
    async def on_raw_reaction_add(self, payload):
        user = payload.member
        guild = user.guild
        channel = guild.get_channel(payload.channel_id)

        if user == self.bot.user or isinstance(channel, discord.DMChannel):
            return

        reaction_emoji = str(payload.emoji)        
        # msg = await channel.fetch_message(payload.message_id)
        msg = await self.messages_util.get_message(channel, payload.message_id)

        if reaction_emoji == self.thread_emoji:
            ctx = await self.bot.get_context(msg, cls=commands.Context)
            await self.thread_start(ctx, payload.message_id)

            await msg.remove_reaction(self.thread_emoji, user)


def setup(bot):
    bot.add_cog(Utility(bot))
