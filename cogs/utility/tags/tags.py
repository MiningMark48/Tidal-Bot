from discord.ext import commands
from fuzzywuzzy import process as fwp

import cogs.utility.tags.tagconf as tc

from util.data.guild_data import GuildData


class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tags = {}

    @commands.Cog.listener("on_ready")
    async def on_ready(self):
        """Load JSON tags when ready"""
        tc.backup_data()
        self.tags = tc.get_data()

    @commands.command(name="settag", aliases=["edittag", "newtag"])
    @commands.cooldown(1, 5)
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def tag_set(self, ctx, tag_name: str, *, message: str):
        """
        Create a new bot tag.
        """

        tag_name = tag_name.lower()
        message = message[:1900]

        GuildData(str(ctx.guild.id)).tags.set(tag_name, message)

        await ctx.send(f"Set tag `{tag_name}` to `{message}`.")

    @commands.command(name="deletetag", aliases=["deltag", "tagdelete"])
    @commands.cooldown(1, 5)
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def tag_delete(self, ctx, *, tag_name: str):
        """
        Delete a bot tag.
        """
        tag_name = tag_name.lower()

        result = GuildData(str(ctx.guild.id)).tags.delete(tag_name)
        if result:
            await ctx.send(f"Deleted tag `{tag_name}`.")
        else:
            await ctx.send("Invalid tag!")

    @commands.command(name="taglist", aliases=["listtags", "tags"])
    @commands.cooldown(1, 3)
    @commands.guild_only()
    async def tag_list(self, ctx):
        """
        List available tags for the server.
        """
        guild_tags = GuildData(str(ctx.guild.id)).tags.fetch_all()

        if not len(guild_tags) > 0:
            await ctx.send("No tags available!")
            return

        tags = f"{ctx.guild.name} Server Tags\n\n"
        for t in sorted(guild_tags):
            value = t[2]
            value = value.replace("\n", "")
            tags += f"[{t[1]}] {value[:100]}{'...' if len(value) > 100 else ''}\n"

        parts = [(tags[i:i + 750]) for i in range(0, len(tags), 750)]
        for part in parts:
            part = part.replace("```", "")
            await ctx.send(f"```{part}```")

    @commands.command(name="tagsearch", aliases=["searchtag"])
    @commands.cooldown(1, 3)
    @commands.guild_only()
    async def tag_search(self, ctx, *, tag_name: str):
        """
        Search for a tag.
        """
        try:

            search_results = self.handle_search(ctx, tag_name)

            results_txt = f"Tag Search Results ({tag_name})\n\n"
            for (res, ratio) in search_results:
                results_txt += f"{res}\n"

            await ctx.send(f"```{results_txt}```")

        except KeyError:
            await ctx.send("No tags available!")

    @commands.command()
    @commands.cooldown(1, 3)
    @commands.guild_only()
    async def tag(self, ctx, *, tag_name: str):
        """
        Call a bot tag.
        """

        tag_name = tag_name.lower()

        if not str(ctx.guild.id) in self.tags:
            await ctx.send("No tags available!")
            return

        try:
            response = self.tags[str(ctx.guild.id)][tag_name]

            if response:
                response = self.handle_variables(response, ctx)
                await ctx.send(response)
        except KeyError:
            search_results = self.handle_search(ctx, tag_name)[:3]

            results_txt = ""
            for (res, ratio) in search_results:
                results_txt += f"{res}\n"

            await ctx.send(f"Couldn't find that tag. Did you mean one of the following?\n```\n{results_txt}\n```")

    @commands.command(name="tagvariables", aliases=["tagvars", "variables", "vars"])
    @commands.cooldown(1, 3)
    @commands.guild_only()
    async def tag_variables(self, ctx):
        """
        Get the list of supported tag variables.

        Tag variables are parts of a string that get replace by specific data.
        """

        variables = self.get_variables(ctx)

        vs = f"Tag Variables\n\n"
        for v in sorted(variables):
            vs += f"[{v}] Ex: {variables[str(v)]}\n"

        parts = [(vs[i:i + 750]) for i in range(0, len(vs), 750)]
        for part in parts:
            await ctx.send(f"```{part}```")

    @staticmethod
    def get_variables(ctx):
        variables = {
            "author": ctx.author.display_name,
            "author_id": ctx.author.id,
            "channel": ctx.channel.name,
            "command_key": ctx.prefix,
            "server_id": ctx.guild.id,
            "server_name": ctx.guild.name
        }

        return variables

    def handle_variables(self, message, ctx):
        variables = self.get_variables(ctx)

        def to_key(v_):
            return f"${{{v_}}}"

        for v in variables:
            message = message.replace(to_key(v), str(variables[v]))

        return message

    def handle_search(self, ctx, tag_name):
        options = []
        for tag in self.tags[str(ctx.guild.id)]:
            options.append(tag)

        search_results = fwp.extract(tag_name, options)

        return search_results


def setup(bot):
    bot.add_cog(Tags(bot))
