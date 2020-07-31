import aiohttp
import discord
from discord.ext import commands

from util.config import BotConfig


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = BotConfig().get_api_key('alphavantage')

    @commands.command(aliases=['btc'])
    @commands.cooldown(1, 3.5)
    async def bitcoin(self, ctx):
        """
        Get info for Bitcoin (BTC)
        """
        async with ctx.typing():
            try:
                base_url = "https://www.alphavantage.co/query"
                payload = {"function": "DIGITAL_CURRENCY_DAILY", "symbol": "BTC", "market": "USD",
                           "apikey": self.api_key}

                async with aiohttp.ClientSession() as session:
                    async with session.get(base_url, params=payload) as r:
                        data = await r.json()

                        if 'Error Message' in data:
                            await ctx.send("Invalid symbol!")
                            return

                        time_series = data['Time Series (Digital Currency Daily)']
                        date = next(iter(time_series))
                        latest = time_series[date]

                        embed = discord.Embed(title=f"Crypto | BTC", color=0xf7931b)
                        embed.timestamp = ctx.message.created_at
                        embed.set_footer(text="Via AlphaVantage")
                        embed.add_field(name="Date", value=date, inline=False)
                        embed.add_field(name="Open", value="${}".format(latest['1a. open (USD)'][:-6]))
                        embed.add_field(name="Close", value="${}".format(latest['4a. close (USD)'][:-6]))
                        embed.add_field(name="High", value="${}".format(latest['2a. high (USD)'][:-6]))
                        embed.add_field(name="Low", value="${}".format(latest['3a. low (USD)'][:-6]))

                        await ctx.send(embed=embed)

            except IndexError:
                await ctx.send("No search results found!")
            except Exception as e:
                await ctx.send(f"An error occurred!\n`{e}`")

    @commands.command(aliases=['stocks'])
    @commands.cooldown(1, 3.5)
    async def stock(self, ctx, symbol: str):
        """
        Get Stock info for a specific Symbol
        """
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

                        embed = discord.Embed(title=f"Stock | {symbol.upper()}", color=0x0087ba)
                        embed.timestamp = ctx.message.created_at
                        embed.set_footer(text="Via AlphaVantage")
                        embed.add_field(name="Date", value=date, inline=False)
                        embed.add_field(name="Open", value="${}".format(latest['1. open'][:-2]))
                        embed.add_field(name="Close", value="${}".format(latest['4. close'][:-2]))
                        embed.add_field(name="High", value="${}".format(latest['2. high'][:-2]))
                        embed.add_field(name="Low", value="${}".format(latest['3. low'][:-2]))

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

                        embed = discord.Embed(title=f"'{query}' | Best Match Symbol", color=0x86d9f3)
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
