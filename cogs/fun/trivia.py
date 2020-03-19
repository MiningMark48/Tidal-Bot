import asyncio
import html
import json
import random
import typing

import discord
import requests
from discord.ext import commands


# import cogs.checks as cks


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.trivia_messages = []
        self.new_trivia = []

    @commands.command()
    async def trivia(self, ctx, time: typing.Optional[int] = 10, difficulty="random"):
        """
        Answer some trivia!
        
        Usage: trivia [time (seconds)] [random|easy|medium|hard] 
        """
        time = max(0, min(time, 60))
        d = difficulty
        if difficulty == "random":
            num = random.randint(0, 2)
            d = "easy" if num == 0 else ("medium" if num == 1 else "hard")
        base_url = f'https://opentdb.com/api.php?amount=1&type=multiple&difficulty={d}'
        url = requests.get(base_url)
        data = json.loads(url.text)
        item = data["results"][0]
        correct_answer = item["correct_answer"]
        answers = { correct_answer: "correct" }
        for ans in item["incorrect_answers"]:
            answers[ans] = "incorrect"
        answers_list = list(answers.keys())
        random.shuffle(answers_list)

        embed = discord.Embed(title=html.unescape(item["question"]), color=ctx.message.author.top_role.color)
        for ans in answers_list:
            embed.add_field(name="‎", value=f'**{getChoice(answers_list, ans)})** {html.unescape(ans)}', inline=False)
        embed.add_field(name="‎", value="‎", inline=False)
        embed.add_field(name="Category", value=item['category'])
        embed.add_field(name="Difficulty", value=item['difficulty'].capitalize())
        embed.add_field(name="Time", value=f'{time} seconds')
        msg = await ctx.send(embed=embed)

        await msg.add_reaction("🇦")
        await msg.add_reaction("🇧")
        await msg.add_reaction("🇨")
        await msg.add_reaction("🇩")

        self.trivia_messages.append(msg.id)
        await asyncio.sleep(time)
        self.trivia_messages.remove(msg.id)

        try:
            re_msg = await ctx.channel.fetch_message(msg.id)
            users_correct = []

            for reac in re_msg.reactions:
                if re_msg.reactions.index(reac) == answers_list.index(correct_answer):
                    async for usr in reac.users():
                        if not usr.bot:
                            users_correct.append(usr)

            await msg.clear_reactions()

            if users_correct:
                amt_crt = len(users_correct)
                correct_list = ', '.join(x.name for x in users_correct)
                # await ctx.send(f':white_check_mark:  **Correct:** {correct_list}')
                correct_message = f'**there {"was" if amt_crt == 1 else "were"} {amt_crt} correct answer{"s" if not amt_crt == 1 else ""}:** *{correct_list}*'
            else:
                # await ctx.send('but nobody got that correct!')
                correct_message = 'but nobody got that correct!'
            await ctx.send(f'{":white_check_mark: " if users_correct else ""}The correct answer was `{getChoice(answers_list, correct_answer)}) {html.unescape(correct_answer)}`, {correct_message}')

            await ctx.send('Click ❓ for a random trivia question.', delete_after=10)
            await msg.add_reaction('❓')
            self.new_trivia.append(msg.id)

        except discord.errors.NotFound:
            print("Message deleted, skipping trivia result.")

    @commands.Cog.listener("on_raw_reaction_add")
    async def on_raw_reaction_add(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        rmsg = await channel.fetch_message(payload.message_id)
        if rmsg.id in self.trivia_messages:
            reaction_emoji = str(payload.emoji)
            user = self.bot.get_user(payload.user_id)
            for reac in rmsg.reactions:
                if not reac.emoji == reaction_emoji:
                    users = await reac.users().flatten()
                    if user in users and not user == self.bot.user:
                        await reac.remove(user)
        if rmsg.id in self.new_trivia:
            reaction_emoji = str(payload.emoji)
            user = self.bot.get_user(payload.user_id)
            if reaction_emoji == '❓':
                if not user == self.bot.user:
                    ctx = await self.bot.get_context(rmsg)
                    cmd = self.bot.get_command("trivia")
                    self.new_trivia.remove(rmsg.id)
                    await rmsg.clear_reactions()
                    await ctx.invoke(cmd)


def getChoice(lst, a):
    num = lst.index(a)
    if num == 0:
        return "A"
    elif num == 1:
        return "B"
    elif num == 2:
        return "C"
    else:
        return "D"


def setup(bot):
    bot.add_cog(Fun(bot))
