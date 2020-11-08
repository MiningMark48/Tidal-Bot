from discord.ext import commands
from fuzzywuzzy import process as fwp


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.options = self.get_options(self.bot.commands)
        print(len(self.options), self.options)

    @commands.command(name="commandsearch", aliases=["cmdsearch", "search"])
    @commands.cooldown(1, 3)
    async def command_search(self, ctx, *, query: str):
        """
        Search for a command
        """

        search_results = self.handle_search(query)

        if len(search_results) <= 0:
            await ctx.send("No search results found!")
            return

        results_txt = f"Command Search Results ({query})\n\n"
        for (res, _) in search_results:
            results_txt += f"{res}\n"

        await ctx.send(f"```{results_txt}```")

    @staticmethod
    def get_options(cmds):
        options = []

        for cmd in cmds:
            options.append(cmd.name)
            # options.append(f"'{cmd.name}' : {cmd.help}")

            for alias in cmd.aliases:
                options.append(alias)

            if isinstance(cmd, commands.Group):
                options.append(c.name for c in cmd.walk_commands())

        return options

    def handle_search(self, query):
        search_results = fwp.extract(query, self.options)
        return search_results


def setup(bot):
    bot.add_cog(Utility(bot))
