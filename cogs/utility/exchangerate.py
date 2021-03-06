import aiohttp
import discord
from discord.ext import commands
from discord import Color

from util.config import BotConfig


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = BotConfig().get_api_key('alphavantage')

    @commands.command(name="exchangerate", aliases=['exchange', 'convertcurrency'])
    @commands.cooldown(1, 3)
    async def exchange_rate(self, ctx, from_currency: str, to_currency: str, amount=1):
        """
        Convert one currency to another
        i.e. USD -> CAD, BTC -> CAD
        """

        amount = max(0.01, amount)

        async with ctx.typing():

            try:
                base_url = "https://www.alphavantage.co/query"
                payload_exchange = {"function": "CURRENCY_EXCHANGE_RATE", "from_currency": from_currency, "to_currency": to_currency,
                            "apikey": self.api_key}

                embed = discord.Embed(title=f"Exchange | {from_currency.upper()} to {to_currency.upper()}", color=Color.dark_theme())
                embed.timestamp = ctx.message.created_at
                embed.set_footer(text="Via AlphaVantage")

                async with aiohttp.ClientSession() as session:
                    async with session.get(base_url, params=payload_exchange) as r:
                        data = await r.json()

                        if 'Error Message' in data:
                            await ctx.send("Invalid symbol!")
                            return

                        rate_data = data['Realtime Currency Exchange Rate']
                        
                        # decimal_amt = 2
                        # decimal_trim = (8 - decimal_amt) * -1

                        exchange_rate = float(rate_data['5. Exchange Rate'])
                        exchange_amt = exchange_rate * amount

                        embed.add_field(name=rate_data['2. From_Currency Name'], value=amount)
                        embed.add_field(name=rate_data['4. To_Currency Name'], value=round(exchange_amt, 2))

                await ctx.send(embed=embed)

            except IndexError:
                await ctx.send("No search results found!")
            except Exception as e:
                await ctx.send(f"An error occurred!\n`{e}`")


def setup(bot):
    bot.add_cog(Utility(bot))
