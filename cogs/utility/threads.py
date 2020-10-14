import copy
import typing

import discord
from discord.ext import commands

from util.decorators import delete_original


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.threads_cat_name = "Threads"

    @commands.group(aliases=["threads"])
    async def thread(self, ctx):
        """
        Channel Threads, until added officially by Discord

        Note: This is experimental, use with caution!
        """

        if ctx.invoked_subcommand is None:
            await ctx.send(f"Invalid subcommand! ")

            msg = copy.copy(ctx.message)
            msg.content = f"{ctx.prefix}help {ctx.command}"
            new_ctx = await self.bot.get_context(msg, cls=type(ctx))
            await self.bot.invoke(new_ctx)

    @thread.command(aliases=["begin"])
    @delete_original()
    async def start(self, ctx, msg_id: typing.Optional[str]):
        """
        Start a thread based on the last sent message or a message ID.
        """

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

    @thread.command(aliases=["stop"])
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
    @delete_original()
    async def rename(self, ctx, name: str):
        """
        Rename a thread.
        """

        async def rename():
            # await ctx.channel.delete(reason="End Thread")
            await ctx.channel.edit(name=f"thread-{name}")
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


def setup(bot):
    bot.add_cog(Utility(bot))
