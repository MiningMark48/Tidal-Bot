import asyncio
from collections import defaultdict

import discord
from discord.ext import commands


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.scale_messages = []
        self.user_answers = {}

    @commands.command()
    @commands.guild_only()
    async def scale(self, ctx, question: str, time: int):
        """
        Create a 'scale' question

        Usage: scale "<Question>" <Time (minutes)>
        """

        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

        embed = discord.Embed(title=question, color=ctx.message.author.top_role.color)

        embed.description = "...on a scale of 1 to 5\n\n" \
                            "1 is low/least \n" \
                            "5 is high/most"

        embed.add_field(name="Time", value=("∞" if time == -1 else f'{time} minute{"s" if time > 1 else ""}'),
                        inline=False)
        embed.set_footer(text=f"Created by {ctx.author.name}")
        msg = await ctx.send(embed=embed)

        await msg.add_reaction("1️⃣")
        await msg.add_reaction("2️⃣")
        await msg.add_reaction("3️⃣")
        await msg.add_reaction("4️⃣")
        await msg.add_reaction("5️⃣")

        if 0 < time <= 120:
            self.scale_messages.append(msg.id)
            await asyncio.sleep(time * 60)
            self.scale_messages.remove(msg.id)

            try:
                await msg.clear_reactions()

                total = len(self.user_answers)
                counter = defaultdict(int)
                for v in self.user_answers.values():
                    counter[v] += 1

                c = {"1": counter["1️⃣"], "2": counter["2️⃣"], "3": counter["3️⃣"], "4": counter["4️⃣"],
                     "5": counter["5️⃣"]}

                embed_results = discord.Embed(title=f'Results: "{question}"', color=ctx.message.author.top_role.color)

                embed_results.description = "1 is low/least\n" \
                                            "5 is high/most"

                embed_results.add_field(name=f"1️⃣", value=get_result_msg(c['1'], total), inline=False)
                embed_results.add_field(name=f"2️⃣", value=get_result_msg(c['2'], total), inline=False)
                embed_results.add_field(name=f"3️⃣", value=get_result_msg(c['3'], total), inline=False)
                embed_results.add_field(name=f"4️⃣", value=get_result_msg(c['4'], total), inline=False)
                embed_results.add_field(name=f"5️⃣", value=get_result_msg(c['5'], total), inline=False)

                await msg.edit(embed=embed_results)
            except discord.errors.NotFound:
                print("Message deleted, skipping poll result.")

    @commands.Cog.listener("on_raw_reaction_add")
    async def on_raw_reaction_add(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        try:
            rmsg = await channel.fetch_message(payload.message_id)
            if rmsg.id in self.scale_messages:
                reaction_emoji = str(payload.emoji)
                user = self.bot.get_user(payload.user_id)
                for reac in rmsg.reactions:
                    if not user == self.bot.user:
                        self.user_answers[user.id] = reaction_emoji
                        await reac.remove(user)
        except discord.errors.NotFound:
            pass


def get_result_msg(amt, total):
    return f'{amt} out of {total} ({"0" if amt == 0 else round(amt/total*100)}%)'


def setup(bot):
    bot.add_cog(Utility(bot))
