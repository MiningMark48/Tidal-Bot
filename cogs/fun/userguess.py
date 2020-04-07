import asyncio
import random
import string

import discord
from discord.colour import Color
from discord.ext import commands
import time


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="userguess", aliases=["ug"])
    @commands.guild_only()
    @commands.cooldown(2, 5)
    async def user_guess(self, ctx):
        """
        Guess a user in the server based on their avatar.
        """

        def check(m):
            return m.channel == ctx.channel

        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

        rand_user = random.choice(ctx.guild.members)

        embed = discord.Embed(title="User Guess", color=Color.blurple())
        embed.description = f"Guess who the user is based on their avatar. You have **15** seconds."
        embed.set_image(url=rand_user.avatar_url_as(size=256))
        embed.set_footer(text="Guess their display name or nickname.")
        msg = await ctx.send(embed=embed)

        start_time = time.time()
        while True:
            if time.time() >= start_time + 15:
                embed.description = f"Time ran out, the user was **{rand_user.display_name}**."
                await msg.edit(embed=embed)
                break

            try:
                guess_msg = await self.bot.wait_for('message', check=check, timeout=15)
            except asyncio.TimeoutError:
                embed.description = f"Time ran out, the user was **{rand_user.display_name}**."
                await msg.edit(embed=embed)
                break

            guess = guess_msg.clean_content.lower()

            printable = set(string.printable)
            name = ''.join(filter(lambda x: x in printable, rand_user.name)).lower()

            nick = rand_user.nick
            if nick:
                nick = ''.join(filter(lambda x: x in printable, nick)).lower()

            if guess == name or guess == nick:
                embed.description = f"{guess_msg.author.mention} guessed correctly! " \
                                    f"The user was **{rand_user.display_name}**!"
                await msg.edit(embed=embed)
                break


def setup(bot):
    bot.add_cog(Fun(bot))
