import datetime
from io import BytesIO

import discord
import matplotlib.pyplot as plt
import numpy as np
import requests
from discord.ext import commands


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.index = 0

    @staticmethod
    def fetch_data():
        base_url = f"https://pomber.github.io/covid19/timeseries.json"
        url = requests.get(base_url, timeout=2)
        data = url.json()
        return data

    @commands.command(name="coronastats", aliases=["corona", "covid", "cstats"])
    @commands.cooldown(1, 5)
    async def corona_stats(self, ctx, *countries: str):
        """
        Fetch COVID-19 Data for a specific country

        Note: You can specify up to 10 countries at once.

        Usage: stats "US" "Canada"
        """

        countries = countries[:10]

        if not countries:
            await ctx.send(f"Missing country!\nDo `{ctx.prefix}help stats` for more help.")
            return

        data = self.fetch_data()

        message = ""

        for country in countries:
            try:
                country_data = data[country]

                if country_data:
                    latest = country_data[len(country_data) - 1]

                    heading = f"[{country}]".ljust(len(max(countries, key=len)) + 3, " ")

                    message += f"{heading} " \
                               f"{latest['confirmed']:,} C | " \
                               f"{latest['deaths']:,} D | " \
                               f"{latest['recovered']:,} R\n\n"

            except KeyError:
                message += f"[{country}] N/A\n\n"

        message += "(C=Confirmed, D=Dead, R=Recovered)"

        embed = discord.Embed(title="COVID-19 Cases")
        embed.description = f"```css\n{message}```[Source](https://github.com/pomber/covid19)"

        await ctx.send(embed=embed)

    @commands.command(name="coronaplot", aliases=["covidplot", "cplot"])
    @commands.cooldown(1, 5)
    async def corona_plot(self, ctx, country_1: str, country_2=""):
        """
        Plot COVID-19 Data for a specific country

        Note: This will likely require the use of quotes.

        Usage: plot "US"
        """

        data = self.fetch_data()

        start_date = datetime.datetime(2020, 1, 22)
        end_date = datetime.datetime.today()-datetime.timedelta(days=1)
        t = np.arange(start_date, end_date, datetime.timedelta(days=1))[1:]
        fig, ax = plt.subplots()

        countries = [country_1]
        has_two = country_2 != ""
        if has_two:
            countries.append(country_2)
        for country in countries:
            try:
                country_data = data[country]

                if country_data:

                    # index = 0
                    data_c = []
                    data_d = []
                    data_r = []
                    for t_ in range(0, len(t)):
                        index_country = country_data[t_]
                        data_c.append(index_country['confirmed'])
                        data_d.append(index_country['deaths'])
                        data_r.append(index_country['recovered'])
                        # index += 1
                    country_plot_name = country if has_two else ''
                    ax.plot(t, data_c, label=f"{country_plot_name} Confirmed")
                    ax.plot(t, data_d, label=f"{country_plot_name} Dead", linestyle="--")
                    ax.plot(t, data_r, label=f"{country_plot_name} Recovered", linestyle="-.")

            except KeyError:
                await ctx.send("Invalid Country! You may need to use quotes. Example: `\"US\"`")
                return

        ax.set(xlabel="Time", ylabel="Cases", title=f"COVID-19 Cases | {', '.join(c for c in countries)}")
        ax.grid()
        ax.legend()

        fig.tight_layout()

        final_buffer = BytesIO()
        fig.savefig(final_buffer)

        final_buffer.seek(0)
        file = discord.File(filename=f"chart.png", fp=final_buffer)

        embed = discord.Embed(title=f"COVID-19 Cases")
        embed.set_image(url=f"attachment://chart.png")
        embed.description = f"[Source](https://github.com/pomber/covid19)"

        await ctx.send(embed=embed, file=file)


def setup(bot):
    bot.add_cog(Info(bot))
