import asyncio
from collections import defaultdict

import discord
from discord.ext import commands


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
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

        time = max(min(time, 120), 1)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and len(m.content) <= 100

        embed = discord.Embed(title=question, color=ctx.message.author.top_role.color)
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
            embed.add_field(name="⠀", value=f'{keycap} {content}', inline=True if len(choices) > 5 else False)
        embed.add_field(name="Time", value=("∞" if time == -1 else f'{time} minute{"s" if time > 1 else ""}'),
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

                embed_results = discord.Embed(title=f'Results: "{question}"', color=ctx.message.author.top_role.color)
                for key, content in choices:
                    embed_results.add_field(name=f"{key} {content}", value=get_result_msg(c[key], total),
                                            inline=True if len(choices) > 5 else False)

                await msg.edit(embed=embed_results)
            except discord.errors.NotFound:
                print("Message deleted, skipping poll result.")

    @commands.command()
    @commands.guild_only()
    async def quickpoll(self, ctx, time: int, question: str, *choices: str):
        """
        Quickly, create a poll for people to vote on

        Usage: quickpoll <Time (minutes)> "<Question>" "[Option 1]" "[Option 2]" ...

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

        embed = discord.Embed(title=question, color=ctx.message.author.top_role.color)
        embed.set_footer(text=f"Created by {ctx.author.name}")

        for key, content in choices:
            embed.add_field(name="⠀", value=f'{key} {content}', inline=True if len(choices) > 5 else False)
        embed.add_field(name="Time", value=("∞" if time == -1 else f'{time} minute{"s" if time > 1 else ""}'),
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

                embed_results = discord.Embed(title=f'Results: "{question}"', color=ctx.message.author.top_role.color)
                for key, content in choices:
                    embed_results.add_field(name=f"{key} {content}", value=get_result_msg(c[key], total),
                                            inline=True if len(choices) > 5 else False)

                await msg.edit(embed=embed_results)
            except discord.errors.NotFound:
                print("Message deleted, skipping poll result.")

    @commands.Cog.listener("on_raw_reaction_add")
    async def on_raw_reaction_add(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        try:
            rmsg = await channel.fetch_message(payload.message_id)
            if rmsg.id in self.poll_messages:
                reaction_emoji = str(payload.emoji)
                user = self.bot.get_user(payload.user_id)
                for reac in rmsg.reactions:
                    if not user == self.bot.user:
                        self.user_answers[(rmsg.id, user.id)] = reaction_emoji
                        await reac.remove(user)
        except discord.errors.NotFound:
            pass


def get_result_msg(amt, total):
    return f'{amt} out of {total} ({"0" if amt == 0 else round(amt/total*100)}%)'


def to_emoji(c):
    base = 0x1f1e6
    return chr(base + c)


def setup(bot):
    bot.add_cog(Utility(bot))
