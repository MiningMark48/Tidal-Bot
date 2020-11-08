from discord.ext import commands
from fuzzywuzzy import process as fwp


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.options = None

    @commands.command(name="commandsearch", aliases=["cmdsearch", "search"])
    @commands.cooldown(1, 3)
    async def command_search(self, ctx, *, query: str):
        """
        Search for a command
        """

        # Load if not already loaded
        if self.options is None:
            self.options = self.get_options(self.bot.commands, desc_search=False)
            # print(len(self.options), self.options)

        search_results = self.handle_search(query)

        if len(search_results) <= 0:
            await ctx.send("No search results found!")
            return

        results_txt = f"Command Search Results ({query})\n\n"
        for (res, rat) in search_results:
            if rat == 100:
                res = f"[ {res} ]"
            # results_txt += f"{res}\n"
            results_txt += f"{res} ({rat})\n"

        await ctx.send(f"```{results_txt}```")

    @staticmethod
    def get_options(cmds, desc_search):
        options = []

        for cmd in cmds:
            options.append(str(cmd.name))

            if desc_search:
                options.append(f"'{cmd.name}' : {cmd.help}")  # Description searching

            for alias in cmd.aliases:
                options.append(str(alias))

            if isinstance(cmd, commands.Group):
                for c in cmd.walk_commands():
                    options.append(str(c))

        return options

    def handle_search(self, query):
        search_results = fwp.extract(query, self.options, limit=5)
        return search_results


def setup(bot):
    bot.add_cog(Utility(bot))
