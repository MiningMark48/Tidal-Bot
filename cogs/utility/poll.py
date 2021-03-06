import asyncio
import aiohttp
from dateutil import parser as dt_parser
from collections import defaultdict

import discord
from discord.ext import commands

from util.decorators import delete_original
from util.messages import MessagesUtil


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.messages_util = MessagesUtil(bot)
        self.poll_messages = []
        self.user_answers = {}

    # noinspection PyBroadException
    @commands.command()
    @commands.guild_only()
    async def poll(self, ctx, time: int, *, question: str):
        """
        Interactively, create a poll for people to vote on

        Usage: poll <Time (minutes)> <Question>

        Note:
        You may have up to 20 options.
        If time is less than 1 or more than 120 (2 hours), no timer will be used.
        """

        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and len(m.content) <= 100

        embed = discord.Embed(
            title=question, color=ctx.message.author.top_role.color)
        embed.set_footer(text=f"Created by {ctx.author.name}")

        # Messages that are deleted after poll creation
        messages = [ctx.message]
        choices = []
        for i in range(20):
            messages.append(await ctx.send(f'Say poll option or `{ctx.prefix}publish` to publish poll.'))

            try:
                entry = await self.bot.wait_for('message', check=check, timeout=30)
            except asyncio.TimeoutError:
                break
            messages.append(entry)

            cleaned = entry.clean_content
            if cleaned.startswith(f'{ctx.prefix}publish'):
                break

            choices.append((to_emoji(i), cleaned))

        try:
            await ctx.channel.delete_messages(messages)
        except Exception:
            pass

        for keycap, content in choices:
            embed.add_field(name="⠀", value=f'{keycap} {content}', inline=True if len(
                choices) > 5 else False)
        embed.add_field(name="Time",
                        value=("∞" if time < 0 or time >
                               120 else f'{time} minute{"s" if time > 1 else ""}'),
                        inline=False)

        msg = await ctx.send(embed=embed)

        for emoji, _ in choices:
            await msg.add_reaction(emoji)

        # Post-poll time handling below
        if 0 < time <= 120:
            self.poll_messages.append(msg.id)
            await asyncio.sleep(time * 60)
            # await asyncio.sleep(5)
            self.poll_messages.remove(msg.id)

            try:
                await msg.clear_reactions()

                total = 0
                c = defaultdict(int)
                for k, v in self.user_answers.items():
                    if k[0] == msg.id:
                        c[v] += 1
                        total += 1

                embed_results = discord.Embed(
                    title=f'Results: "{question}"', color=ctx.message.author.top_role.color)
                for key, content in choices:
                    embed_results.add_field(name=f"{key} {content}", value=get_result_msg(c[key], total),
                                            inline=True if len(choices) > 5 else False)

                await msg.edit(embed=embed_results)
            except discord.errors.NotFound:
                print("Message deleted, skipping poll result.")

    @commands.command(name="quickpoll")
    @commands.guild_only()
    async def quick_poll(self, ctx, time: int, question: str, *choices: str):
        """
        Quickly, create a poll for people to vote on

        Usage: quickpoll <Time (minutes)> "<Question>" "<Option 1>" "<Option 2>" ...

        Note:
        You may have up to 20 options.
        If time is less than 1 or more than 120 (2 hours), no timer will be used.
        """

        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

        if len(choices) < 2:
            return await ctx.send('You need at least 2 choices.')
        elif len(choices) > 20:
            return await ctx.send('You can only have up to 20 choices.')

        # question = questions_and_choices[0]
        choices = [(to_emoji(e), v) for e, v in enumerate(choices)]

        embed = discord.Embed(
            title=question, color=ctx.message.author.top_role.color)
        embed.set_footer(text=f"Created by {ctx.author.name}")

        for key, content in choices:
            embed.add_field(name="⠀", value=f'{key} {content}', inline=True if len(
                choices) > 5 else False)
        embed.add_field(name="Time",
                        value=("∞" if time < 0 or time >
                               120 else f'{time} minute{"s" if time > 1 else ""}'),
                        inline=False)

        msg = await ctx.send(embed=embed)
        for emoji, _ in choices:
            await msg.add_reaction(emoji)

        # Post-poll time handling below
        if 0 < time <= 120:
            self.poll_messages.append(msg.id)
            await asyncio.sleep(time * 60)
            self.poll_messages.remove(msg.id)

            try:
                await msg.clear_reactions()

                total = 0
                c = defaultdict(int)
                for k, v in self.user_answers.items():
                    if k[0] == msg.id:
                        c[v] += 1
                        total += 1

                embed_results = discord.Embed(
                    title=f'Results: "{question}"', color=ctx.message.author.top_role.color)
                for key, content in choices:
                    embed_results.add_field(name=f"{key} {content}", value=get_result_msg(c[key], total),
                                            inline=True if len(choices) > 5 else False)

                await msg.edit(embed=embed_results)
            except discord.errors.NotFound:
                print("Message deleted, skipping poll result.")

    @commands.command(name="quickpolldef", aliases=["qpd"])
    @commands.guild_only()
    async def quick_poll_defaults(self, ctx, time: int, question: str, default_choice: str):
        """
        Quickly, create a poll for people to vote on using default choices

        Usage: quickpoll <Time (minutes)> "<Question>" "<Default Choice>"

        Default Choices: yesno (Yes/No), truefalse (True/False), scale15 (1/2/3/4/5), abcd (A/B/C/D)

        Note:
        If time is less than 1 or more than 120 (2 hours), no timer will be used.
        """

        default_choice = default_choice.lower()

        if default_choice in ["yesno", "yn"]:
            await self.quick_poll(ctx, time, question, "Yes", "No")
        elif default_choice in ["truefalse", "tf"]:
            await self.quick_poll(ctx, time, question, "True", "False")
        elif default_choice in ["scale15", "s15"]:
            await self.quick_poll(ctx, time, question, "1", "2", "3", "4", "5")
        elif default_choice in ["abcd"]:
            await self.quick_poll(ctx, time, question, "A", "B", "C", "D")
        else:
            await ctx.send("Default choice not found!", delete_after=10)

    @commands.Cog.listener("on_raw_reaction_add")
    async def on_raw_reaction_add(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        try:
            # rmsg = await channel.fetch_message(payload.message_id)
            rmsg = await self.messages_util.get_message(channel, payload.message_id)
            if rmsg.id in self.poll_messages:
                reaction_emoji = str(payload.emoji)
                user = self.bot.get_user(payload.user_id)
                for reac in rmsg.reactions:
                    if not user == self.bot.user:
                        self.user_answers[(rmsg.id, user.id)] = reaction_emoji
                        await reac.remove(user)
        except discord.errors.NotFound:
            pass

    @commands.command(aliases=["sp"])
    @commands.guild_only()
    @commands.cooldown(1, 30)
    @delete_original()
    async def strawpoll(self, ctx, question: str, *choices: str):
        """
        Create a Strawpoll
        """

        choices = list(choices)  # Choices tuple to list

        # Create poll JSON
        poll_data = {
            "poll": {
                "title": question,
                "answers": choices,
                "priv": True,
                "co": False,
                "ma": False,
                "vpn": True
            }
        }

        # Post to Strawpoll.com API
        base_url = "https://strawpoll.com/api/poll"
        async with aiohttp.ClientSession() as session:
            async with session.post(base_url, json=poll_data) as r:
                data = await r.json()
                if data['success'] == 1:
                    poll_link = f"https://strawpoll.com/{data['content_id']}"
                    await ctx.send("{}, here you go!\n{}".format(ctx.author.mention, poll_link))
                else:
                    await ctx.send("An error has occurred. Please try again later.")

    @commands.command(name="strawpollresults", aliases=["spresults", "spr"])
    @commands.guild_only()
    @commands.cooldown(1, 5)
    @delete_original()
    async def strawpoll_results(self, ctx, poll_id: str):
        """
        Get the results from a Strawpoll
        """

        # Post to Strawpoll.com API
        base_url = f"https://strawpoll.com/api/poll/{poll_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url) as r:
                data = await r.json()
                if data['success'] == 1:
                    poll_link = f"https://strawpoll.com/{poll_id}"
                    poll_content = data['content']
                    poll_data = poll_content['poll']

                    embed = discord.Embed(
                        title=f"Strawpoll: {poll_data['title']}", url=poll_link, color=0x3eb991)

                    answers = poll_data['poll_answers']
                    for answer in answers:
                        embed.add_field(name=answer['answer'], value=get_result_msg(
                            answer['votes'], poll_data['total_votes']), inline=True if len(answers) > 5 else False)

                    embed.timestamp = dt_parser.parse(poll_content['created_at'])
                    embed.set_footer(text=f"ID: {poll_id}")

                    await ctx.send(embed=embed)

                else:
                    await ctx.send("Invalid ID!")


def get_result_msg(amt, total):
    return f'{amt} out of {total} ({"0" if amt == 0 else round(amt/total*100)}%)'


def to_emoji(c):
    base = 0x1f1e6
    return chr(base + c)


def setup(bot):
    bot.add_cog(Utility(bot))
