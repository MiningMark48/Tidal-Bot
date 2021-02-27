import aiohttp
import discord
from discord.ext import commands
from discord import Color

from util.config import BotConfig


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = BotConfig().get_api_key('alphavantage')

    @commands.command(aliases=['cryptocurrency'])
    @commands.cooldown(1, 3)
    async def crypto(self, ctx, symbol: str, decimal_amt=4):
        """
        Get info for a Cryptocurrency by symbol
        i.e. BTC (Bitcoin), DOGE (Dogecoin), XLM (Stellar Lumens)
        """

        decimal_amt = max(2, min(7, decimal_amt))

        async with ctx.typing():

            

            try:
                base_url = "https://www.alphavantage.co/query"
                payload_main = {"function": "DIGITAL_CURRENCY_DAILY", "symbol": symbol, "market": "USD",
                           "apikey": self.api_key}
                payload_exchange = {"function": "CURRENCY_EXCHANGE_RATE", "from_currency": symbol, "to_currency": "USD",
                            "apikey": self.api_key}

                embed = discord.Embed(title=f"Crypto | {symbol.upper()}", color=Color.dark_theme())
                embed.timestamp = ctx.message.created_at
                embed.set_footer(text="Via AlphaVantage")
                embed.description = "**Note:** All values are in USD."

                async with aiohttp.ClientSession() as session:
                    async with session.get(base_url, params=payload_main) as r:
                        data = await r.json()

                        if 'Error Message' in data:
                            await ctx.send("Invalid symbol!")
                            return

                        time_series = data['Time Series (Digital Currency Daily)']
                        date = next(iter(time_series))
                        latest = time_series[date]

                        embed.add_field(name="Date", value=date, inline=False)

                        decimal_trim = (8 - decimal_amt) * -1
                        embed.add_field(name="Open", value="${}".format(latest['1a. open (USD)'][:decimal_trim]))
                        embed.add_field(name="Close", value="${}".format(latest['4a. close (USD)'][:decimal_trim]))
                        embed.add_field(name="High", value="${}".format(latest['2a. high (USD)'][:decimal_trim]))
                        embed.add_field(name="Low", value="${}".format(latest['3a. low (USD)'][:decimal_trim]))

                async with aiohttp.ClientSession() as session:
                    async with session.get(base_url, params=payload_exchange) as r:
                        data = await r.json()

                        if 'Error Message' in data:
                            await ctx.send("Invalid symbol!")
                            return

                        rate_data = data['Realtime Currency Exchange Rate']

                        decimal_trim = (8 - decimal_amt) * -1
                        embed.add_field(name="Current Exchange", value="${}".format(rate_data['5. Exchange Rate'][:decimal_trim]), inline=False)

                await ctx.send(embed=embed)

            except IndexError:
                await ctx.send("No search results found!")
            except Exception as e:
                await ctx.send(f"An error occurred!\n`{e}`")

    @commands.command(aliases=['stocks'])
    @commands.cooldown(1, 3.5)
    async def stock(self, ctx, symbol: str, decimal_amt=2):
        """
        Get Stock info for a specific Symbol
        """

        decimal_amt = max(2, min(3, decimal_amt))

        async with ctx.typing():
            try:
                base_url = "https://www.alphavantage.co/query"
                payload = {"function": "TIME_SERIES_DAILY", "symbol": symbol, "apikey": self.api_key}

                async with aiohttp.ClientSession() as session:
                    async with session.get(base_url, params=payload) as r:
                        data = await r.json()

                        if 'Error Message' in data:
                            await ctx.send("Invalid symbol!")
                            return

                        time_series = data['Time Series (Daily)']
                        date = next(iter(time_series))
                        latest = time_series[date]

                        embed = discord.Embed(title=f"Stock | {symbol.upper()}", color=Color.dark_theme())
                        embed.timestamp = ctx.message.created_at
                        embed.set_footer(text="Via AlphaVantage")
                        embed.add_field(name="Date", value=date, inline=False)

                        decimal_trim = (4 - decimal_amt) * -1
                        embed.add_field(name="Open", value="${}".format(latest['1. open'][:decimal_trim]))
                        embed.add_field(name="Close", value="${}".format(latest['4. close'][:decimal_trim]))
                        embed.add_field(name="High", value="${}".format(latest['2. high'][:decimal_trim]))
                        embed.add_field(name="Low", value="${}".format(latest['3. low'][:decimal_trim]))

                        await ctx.send(embed=embed)

            except IndexError:
                await ctx.send("No search results found!")
            except Exception as e:
                await ctx.send(f"An error occurred!\n`{e}`")

    @commands.command(name='symbolsearch', aliases=['lookupsymbol'])
    @commands.cooldown(1, 3.5)
    async def symbol_search(self, ctx, query: str):
        """
        Lookup a stock symbol
        """
        async with ctx.typing():
            try:
                base_url = "https://www.alphavantage.co/query"
                payload = {"function": "SYMBOL_SEARCH", "keywords": query, "apikey": self.api_key}

                async with aiohttp.ClientSession() as session:
                    async with session.get(base_url, params=payload) as r:
                        data = await r.json()

                        matches = data['bestMatches']

                        if len(matches) == 0:
                            await ctx.send("No search results found!")
                            return

                        best = matches[0]

                        embed = discord.Embed(title=f"'{query}' | Best Match Symbol", color=Color.dark_theme())
                        embed.timestamp = ctx.message.created_at
                        embed.set_footer(text="Via AlphaVantage")
                        embed.add_field(name="Symbol", value=best['1. symbol'])
                        embed.add_field(name="Name", value=best['2. name'])
                        embed.add_field(name="Type", value=best['3. type'])
                        embed.add_field(name="Region", value=best['4. region'])

                        await ctx.send(embed=embed)

            except IndexError:
                await ctx.send("No search results found!")
            except Exception as e:
                await ctx.send(f"An error occurred!\n`{e}`")


def setup(bot):
    bot.add_cog(Info(bot))
