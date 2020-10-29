from discord.ext import commands


class Support(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="buymeacoffee", aliases=["coffee"])
    async def buy_me_a_coffee(self, ctx):
        """Help support development by buying me a coffee - err - fry"""
        link = "https://www.buymeacoffee.com/miningmark48"
        await ctx.send(f"{ctx.author.mention}, {link}")

    @commands.command(name="cashapp")
    async def cash_app(self, ctx):
        """Help support development via CashApp"""
        link = "https://cash.app/$MiningMark48"
        await ctx.send(f"{ctx.author.mention}, {link}")

    # @commands.command(hidden=True)
    # async def patreon(self, ctx):
    #     """Help support development via Patreon"""
    #     link = "N/A"
    #     await ctx.send(f"{ctx.author.mention}, {link}")


def setup(bot):
    bot.add_cog(Support(bot))
