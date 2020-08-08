import asyncio
import random

import discord
from discord.colour import Color
from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.new_game = []

    @commands.command(name="higherlower", aliases=["hl"])
    async def higher_lower(self, ctx, number=100):
        """
        Play a higher-lower number guessing game
        """

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and str(m.content).isnumeric()

        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

        rand_num = random.randint(1, number)

        embed = discord.Embed(title="Number Guess", color=Color.dark_gold())
        embed.description = f"Guess a number between **1** and **{number}**."
        msg = await ctx.send(embed=embed, content=f"{ctx.author.mention}, here ya go!")

        tries = 0
        guesses = []
        while True:
            tries += 1

            if tries > number:
                embed.description = f"You should have guessed it by now, the number was **{rand_num}**."
                await msg.edit(embed=embed)
                break

            try:
                guess_msg = await self.bot.wait_for('message', check=check, timeout=20)

            except asyncio.TimeoutError:
                embed.description = f"Time ran out, the number was **{rand_num}**."
                await msg.edit(embed=embed)
                break
            guess = int(guess_msg.clean_content)
            guesses.append(guess)

            try:
                await guess_msg.delete()
            except discord.HTTPException:
                pass

            if guess < rand_num:
                embed.description = f"The number is **higher** than `{guess}`!"
            elif guess > rand_num:
                embed.description = f"The number is **lower** than `{guess}`!"
            else:
                guesses_list = ', '.join(str(g) for g in guesses)
                embed.description = f"Correct! You guessed **{rand_num}** in **{tries}** tries.\n\n" \
                                    f"Your guesses: {guesses_list}"
                await msg.edit(embed=embed)
                break

            await msg.edit(embed=embed)

        # self.new_game.append(msg.id)
        # await msg.add_reaction("🔁")

    # @commands.Cog.listener("on_raw_reaction_add")
    # async def on_raw_reaction_add(self, payload):
    #     guild = self.bot.get_guild(payload.guild_id)
    #     channel = guild.get_channel(payload.channel_id)
    #     rmsg = await channel.fetch_message(payload.message_id)

    #     if rmsg.id in self.new_game:
    #         reaction_emoji = str(payload.emoji)
    #         user = self.bot.get_user(payload.user_id)
    #         if reaction_emoji == '🔁':
    #             if not user == self.bot.user:
    #                 ctx = await self.bot.get_context(rmsg)
    #                 cmd = self.bot.get_command("higherlower")
    #                 self.new_game.remove(rmsg.id)
    #                 await rmsg.clear_reactions()
    #                 await ctx.invoke(cmd)


def setup(bot):
    bot.add_cog(Fun(bot))
