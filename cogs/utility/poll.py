import discord
import asyncio
import typing
from discord.ext import commands
from collections import defaultdict


# import cogs.checks as cks

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.poll_messages = []
        self.user_answers = {}

    @commands.command()
    @commands.guild_only()
    async def poll(self, ctx, question: str, time: int, opt1: typing.Optional[str], opt2: typing.Optional[str],
                   opt3: typing.Optional[str], opt4: typing.Optional[str]):
        """
        Create a poll for people to vote on
        
        Usage: poll "<Question>" <Time (minutes)> "[Option 1]" "[Option 2]" "[Option 3]" "[Option 4]"

        Note: If option 1 and 2 are not given, they default to Yes and No, respectively. 
        Also, if the question or any of the options are a single word, quotes are not needed.
        If time is less than 1 or more than 120 (2 hours), no timer will be used.
        """

        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

        embed = discord.Embed(title=question, color=ctx.message.author.top_role.color)
        if not opt1 or not opt2:
            opt1 = "Yes"
            opt2 = "No"
        embed.add_field(name="-", value=f'🇦  {opt1}', inline=False)
        embed.add_field(name="-", value=f'🇧  {opt2}', inline=False)
        if opt3:
            embed.add_field(name="-", value=f'🇨  {opt3}', inline=False)
        if opt4:
            embed.add_field(name="-", value=f'🇩  {opt4}', inline=False)
        embed.add_field(name="Time", value=("∞" if time == -1 else f'{time} minute{"s" if time > 1 else ""}'),
                        inline=False)
        embed.set_footer(text=f"Created by {ctx.author.name}")
        msg = await ctx.send(embed=embed)

        if opt1:
            await msg.add_reaction("🇦")
        if opt2:
            await msg.add_reaction("🇧")
        if opt3:
            await msg.add_reaction("🇨")
        if opt4:
            await msg.add_reaction("🇩")

        if 0 < time <= 120:
            self.poll_messages.append(msg.id)
            await asyncio.sleep(time * 60)
            self.poll_messages.remove(msg.id)

            try:
                await msg.clear_reactions()

                total = len(self.user_answers)
                counter = defaultdict(int)
                for v in self.user_answers.values():
                    counter[v] += 1

                c = {"a": counter["🇦"], "b": counter["🇧"], "c": counter["🇨"], "d": counter["🇩"]}

                embed_results = discord.Embed(title=f'Results: "{question}"', color=ctx.message.author.top_role.color)
                embed_results.add_field(name=f"🇦  {opt1}", value=get_result_msg(c['a'], total), inline=False)
                embed_results.add_field(name=f"🇧  {opt2}", value=get_result_msg(c['b'], total), inline=False)
                if opt3:
                    embed_results.add_field(name=f"🇨  {opt3}", value=get_result_msg(c['c'], total), inline=False)
                if opt4:
                    embed_results.add_field(name=f"🇩  {opt4}", value=get_result_msg(c['d'], total), inline=False)

                await msg.edit(embed=embed_results)
            except discord.errors.NotFound:
                print("Message deleted, skipping poll result.")

    @commands.Cog.listener("on_raw_reaction_add")
    async def on_raw_reaction_add(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        rmsg = await channel.fetch_message(payload.message_id)
        if rmsg.id in self.poll_messages:
            reaction_emoji = str(payload.emoji)
            user = self.bot.get_user(payload.user_id)
            for reac in rmsg.reactions:
                if not user == self.bot.user:
                    self.user_answers[user.id] = reaction_emoji
                    await reac.remove(user)


def get_result_msg(amt, total):
    return f'{amt} out of {total} ({"0" if amt == 0 else round(amt/total*100)}%)'


def setup(bot):
    bot.add_cog(Utility(bot))
