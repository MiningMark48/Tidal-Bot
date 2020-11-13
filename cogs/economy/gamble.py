import copy
import random

from discord.ext import commands

from util.decorators import delete_original


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.economy = self.get_economy()

    def get_economy(self):
        return self.bot.get_cog("Economy")

    @commands.group()
    @commands.cooldown(1, 2)
    @delete_original()
    async def gamble(self, ctx):
        """Economy: Gamble"""

        if ctx.invoked_subcommand is None:
            await ctx.send(f"Invalid subcommand! ")

            msg = copy.copy(ctx.message)
            msg.content = f"{ctx.prefix}help {ctx.command}"
            new_ctx = await self.bot.get_context(msg, cls=type(ctx))
            await self.bot.invoke(new_ctx)

    @gamble.command(name="coinflip")
    async def gamble_coin_flip(self, ctx, bet: int):
        """Gamble on a coin flip."""

        if self.economy is not None:
            winner = False
            current = self.economy.get_currency(str(ctx.guild.id), str(ctx.author.id))

            if current >= bet:
                self.economy.remove_currency(str(ctx.guild.id), str(ctx.author.id), bet)
                current -= bet
                if random.randint(0, 1) == 0:
                    self.economy.add_currency(str(ctx.guild.id), str(ctx.author.id), bet * 1.5)
                    current += bet
                    winner = True

                await ctx.send(f"You flipped a coin and **{'won' if winner else 'lost'}**! "
                               f"You know have **{str(current)}**.")
            else:
                await ctx.send("You can't afford that!")


def setup(bot):
    bot.add_cog(Economy(bot))
