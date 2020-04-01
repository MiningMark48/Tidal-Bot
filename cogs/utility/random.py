import random

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


def setup(bot):
    bot.add_cog(Utility(bot))

