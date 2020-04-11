import random
import string

from discord.ext import commands


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="coinflip", aliases=["coin", "flipcoin"])
    async def coin_flip(self, ctx):
        """Flip a coin!"""
        flip = random.randint(0, 1)
        await ctx.send(f':moneybag: You flipped a coin and got **{"heads" if flip == 0 else "tails"}**! :moneybag:')

    @commands.command(name="diceroll", aliases=["dice", "rolldice"])
    async def dice_roll(self, ctx, amt=1):
        """Roll a dice!"""
        if 0 < amt <= 25:
            roll = ', '.join(str(random.randint(1, 6)) for x in range(amt))
            await ctx.send(f':game_die: You rolled a die and got... **{roll}**! :game_die:')
        else:
            await ctx.send('Amount must be between **0** and **25**!')

    @commands.command(name="randcard", aliases=["randcards", "card", "cards"])
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

    @commands.command(name="randchoice", aliases=["randc", "randomc"])
    async def rand_choice(self, ctx, *choices: str):
        """Get a random choice from a list of provided choices"""
        if len(choices) < 2:
            await ctx.send("You must have at least **2** choices.")
            return

        choice = random.choice(choices)
        await ctx.send(f"Your random choice is `{choice}`!")

    @commands.command(name="randnum", aliases=["rand", "random"])
    async def rand_num(self, ctx, min: int, max: int, amt=1):
        """Get a random number between two values"""
        if 0 < amt <= 25:
            roll = ', '.join(str(random.randint(min, max)) for x in range(amt))
            await ctx.send(f'Your random number{"s are" if amt > 1 else " is"}... **{roll}**!')
        else:
            await ctx.send('Amount must be between **0** and **25**!')

    @commands.command(name="randtext", aliases=["lorem", "loremipsum"])
    async def rand_text(self, ctx, sentences=5, words_per_sentence=10):
        """Generate random text."""

        sentences = max(min(sentences, 25), 1)
        words_per_sentence = max(min(words_per_sentence, 20), 6)

        sentences_list = []
        for i in range(1, sentences+1):
            words_list = []
            for j in range(random.randint(1, 5), words_per_sentence+1):
                words_list.append(''.join(random.choices(string.ascii_lowercase, k=random.randint(2, 10))))

            sentence = ' '.join(word for word in words_list)
            sentence = sentence.capitalize()
            sentence += "."

            sentences_list.append(sentence)

        final = ' '.join(sentence for sentence in sentences_list)

        parts = [(final[i:i + 1800]) for i in range(0, len(final), 1800)]

        for part in parts:
            await ctx.send(f"```{part}```")


def setup(bot):
    bot.add_cog(Utility(bot))

