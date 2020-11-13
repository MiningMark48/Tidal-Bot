import copy
import random

from discord.ext import commands
from faker import Faker


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=["rand"])
    async def random(self, ctx):
        """Commands that generate random data."""

        if ctx.invoked_subcommand is None:
            await ctx.send(f"Invalid subcommand! ")

            msg = copy.copy(ctx.message)
            msg.content = f"{ctx.prefix}help {ctx.command}"
            new_ctx = await self.bot.get_context(msg, cls=type(ctx))
            await self.bot.invoke(new_ctx)

    @random.command(name="card", aliases=["cards"])
    async def rand_card(self, ctx, amt=1):
        """Draw a random card from a deck"""

        amt = max(min(amt, 52), 1)

        suits = ["Spades", "Clubs", "Hearts", "Diamonds"]
        nums = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]

        cards = []

        def draw_card():
            num = random.choice(nums)
            suit = random.choice(suits)
            card = f"{num} of {suit}"

            if card in cards:
                draw_card()
            else:
                cards.append(card)

        for i in range(0, amt):
            draw_card()

        message = ', '.join(card for card in cards)
        await ctx.send(f"{ctx.author.mention}, here ya go!\n{message}")

    @random.command(name="choice")
    async def rand_choice(self, ctx, *choices: str):
        """Get a random choice from a list of provided choices"""
        if len(choices) < 2:
            await ctx.send("You must have at least **2** choices.")
            return

        choice = random.choice(choices)
        await ctx.send(f"Your random choice is `{choice}`!")

    @random.command(name="coin", aliases=["coinflip", "flipcoin"])
    async def rand_coin(self, ctx):
        """Flip a coin!"""
        flip = random.randint(0, 1)
        await ctx.send(f':moneybag: You flipped a coin and got **{"heads" if flip == 0 else "tails"}**! :moneybag:')

    @random.command(name="dice", aliases=["diceroll", "rolldice"])
    async def rand_dice(self, ctx, amt=1):
        """Roll a dice!"""
        if 0 < amt <= 25:
            roll = ', '.join(str(random.randint(1, 6)) for _ in range(amt))
            await ctx.send(f':game_die: You rolled a die and got... **{roll}**! :game_die:')
        else:
            await ctx.send('Amount must be between **0** and **25**!')

    @random.command(name="number", aliases=["num"])
    async def rand_num(self, ctx, min: int, max: int, amt=1):
        """Get a random number between two values"""
        if 0 < amt <= 25:
            roll = ', '.join(str(random.randint(min, max)) for _ in range(amt))
            await ctx.send(f'Your random number{"s are" if amt > 1 else " is"}... **{roll}**!')
        else:
            await ctx.send('Amount must be between **0** and **25**!')

    @random.command(name="text", aliases=["lorem", "loremipsum"])
    async def rand_text(self, ctx, max_chars=500):
        """Generate random text."""

        max_chars = max(min(max_chars, 1900), 25)

        fake = Faker("en_US")

        text = fake.text(max_nb_chars=max_chars, ext_word_list=None)
        text = text.replace("\n", " ")

        await ctx.send(f"```{text}```")


def setup(bot):
    bot.add_cog(Utility(bot))

