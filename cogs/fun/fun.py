import discord
import random
from discord.ext import commands
from util.spongemock import mockify


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="bubblewrap")
    async def bubble_wrap(self, ctx):
        """Satisfying popping"""
        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

        rows = 10
        columns = 10
        grid = [["||     ||" for n in range(columns)] for n in range(rows)]
        sb = []
        for rws in grid:
            sb.append(''.join(map(str, rws)))
        sb = '\n'.join(sb)

        final = f'{ctx.author.mention}, here\'s your bubble wrap!\n\n' \
                f'{sb}\n\n'

        await ctx.send(final)

    @commands.command(aliases=["coin", "flipcoin"])
    async def coinflip(self, ctx):
        """Flip a coin!"""
        flip = random.randint(0, 1)
        await ctx.send(f':moneybag: You flipped a coin and got **{"heads" if flip == 0 else "tails"}**! :moneybag:')

    @commands.command(aliases=["dice", "rolldice"])
    async def diceroll(self, ctx, amt=1):
        """Roll a dice!"""
        if 0 < amt <= 25:
            roll = ', '.join(str(random.randint(1, 6)) for x in range(amt))
            await ctx.send(f':game_die: You rolled a die and got... **{roll}**! :game_die:')
        else:
            await ctx.send('Amount must be between **0** and **25**!') 

    @commands.command(aliases=["rand", "random"])
    async def randnum(self, ctx, min: int, max: int, amt=1):
        """Get a random number between two values"""
        if 0 < amt <= 25:
            roll = ', '.join(str(random.randint(min, max)) for x in range(amt))
            await ctx.send(f'Your random number is... **{roll}**!')
        else:
            await ctx.send('Amount must be between **0** and **25**!')

    @commands.command()
    async def slap(self, ctx, *, user: str):
        """Slap someone with a fish"""
        await ctx.send(f"*slaps {user} with a fish.* :fish:")

    @commands.command()
    async def mock(self, ctx, *, text: str):
        """spOngEBoB MoCKifY soMe TeXT"""
        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass
        await ctx.send(mockify(text))


def setup(bot):
    bot.add_cog(Fun(bot))

