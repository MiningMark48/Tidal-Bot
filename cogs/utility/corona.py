import requests
from discord.ext import commands


class Utility(commands.Cog):
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
    async def corona_stats(self, ctx, *countries: str):
        """
        Fetch COVID-19 Data for a specific country

        Usage: stats "US" "Canada"
        """

        if not countries:
            await ctx.send(f"Missing country!\nDo `{ctx.prefix}help stats` for more help.")
            return

        data = self.fetch_data()
        # pattern = re.compile(r'\[(c19-)(.*?)\]')
        # topic_matches = re.findall(pattern, channel.topic)

        message = f"COVID-19 Cases\n\n\n"

        for country in countries:
            try:
                country_data = data[country]

                if country_data:
                    latest = country_data[len(country_data) - 1]

                    heading = f"[{country}]".ljust(len(max(countries, key=len)) + 3, " ")

                    message += f"{heading} " \
                               f"{latest['confirmed']} confirmed, " \
                               f"{latest['deaths']} deaths, " \
                               f"{latest['recovered']} recovered\n"

            except KeyError:
                message += f"[{country}] N/A\n"

        # message += "\n\nData Fetched Using: https://github.com/pomber/covid19"

        max_chars = 1900
        msg_parts = [(message[i:i + max_chars]) for i in range(0, len(message), max_chars)]
        for part in msg_parts:
            await ctx.send(f"```css\n{part}```Data Fetched Using: <https://github.com/pomber/covid19>")


def setup(bot):
    bot.add_cog(Utility(bot))
