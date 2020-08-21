import random
import aiohttp
import asyncio
import discord
from discord.ext import commands

from util.decorators import delete_original


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.new_game = []

    @commands.command(name="hangman")
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @delete_original()
    async def hangman(self, ctx):
        """Play a game of Hangman"""

        def check(m):
            return m.author.id == ctx.author.id

        def find(s, ch):
            return [i for i, ltr in enumerate(s) if ltr == ch]

        with open("resources/words.txt", "r") as file:
            words_list = sorted(file.read().split("\n"))

        embed = discord.Embed(title="Hangman", color=0x654321)

        rand_word = random.choice(words_list)

        blanks_list = list('-' * len(rand_word))
        word_blanks = f"**Word:**\n\n{' '.join(x for x in blanks_list)}"
        letters_used = []

        embed.description = word_blanks
        embed.set_footer(text=f"{ctx.author.name}'s Game")

        msg = await ctx.send(embed=embed)

        guessed = False
        tries_left = 10
        while not guessed and tries_left > 0:

            try:
                guess_msg = await self.bot.wait_for('message', check=check, timeout=30)
                await guess_msg.delete()
            except asyncio.TimeoutError:
                embed.description = f"Time ran out, the word was **{rand_word}**."
                await msg.edit(embed=embed)
                break

            try:
                guess = guess_msg.clean_content.lower()[0]
            except IndexError:
                pass

            if guess not in letters_used:
                letters_used.append(guess)

            if guess in rand_word:
                pos = find(rand_word, guess)
                for p in pos:
                    blanks_list[p] = guess
            else:
                tries_left -= 1

            if (''.join(x for x in blanks_list)) == rand_word:
                guessed = True

            word_blanks = f"**Word:**\n\n{' '.join(x for x in blanks_list)}"
            tries_remaining = f"**Tries Left:** {tries_left}"

            embed.description = f"{word_blanks}\n\n{tries_remaining}\n\n**Letters Used:**\n\n{', '.join(x for x in sorted(letters_used))}"

            await msg.edit(embed=embed)

        if guessed:
            embed.description = f"You win! The word was **{rand_word}**."
        elif tries_left == 0:
            embed.description = f"You ran of tries! The word was **{rand_word}**."

        await msg.edit(embed=embed)

        # self.new_game.append(msg.id)
        # await msg.add_reaction("\N{CLOCKWISE RIGHTWARDS AND LEFTWARDS OPEN CIRCLE ARROWS}")

    # @commands.Cog.listener("on_raw_reaction_add")
    # async def on_raw_reaction_add(self, payload):
    #     guild = self.bot.get_guild(payload.guild_id)
    #     channel = guild.get_channel(payload.channel_id)
    #     rmsg = await channel.fetch_message(payload.message_id)

    #     if rmsg.id in self.new_game:
    #         reaction_emoji = str(payload.emoji)
    #         user = self.bot.get_user(payload.user_id)
    #         if reaction_emoji == '\N{CLOCKWISE RIGHTWARDS AND LEFTWARDS OPEN CIRCLE ARROWS}':
    #             if not user == self.bot.user:
    #                 ctx = await self.bot.get_context(rmsg)
    #                 cmd = self.bot.get_command("hangman")
    #                 self.new_game.remove(rmsg.id)
    #                 await rmsg.clear_reactions()
    #                 await ctx.invoke(cmd)

def setup(bot):
    bot.add_cog(Fun(bot))
