from discord.ext import commands
import cogs.utility.tags.tagconf as tc


class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tags = {}

    @commands.Cog.listener("on_ready")
    async def on_ready(self):
        """Load JSON tags when ready"""
        self.tags = tc.get_data()

    @commands.command(name="settag", aliases=["edittag", "newtag"])
    @commands.cooldown(1, 5)
    @commands.guild_only()
    async def tag_set(self, ctx, tag_name: str, *, message: str):
        """
        Create a new bot tag.
        """
        if not str(ctx.guild.id) in self.tags:
            self.tags.update({str(ctx.guild.id): {}})

        tag_name = tag_name.lower()
        message = message[:1900]
        self.tags[str(ctx.guild.id)].update({tag_name: message})
        tc.update_servers(self.tags)
        tc.save_data()
        await ctx.send(f"Set tag `{tag_name}` to `{message}`.")

    @commands.command(name="deletetag", aliases=["deltag", "tagdelete"])
    @commands.cooldown(1, 5)
    @commands.guild_only()
    async def tag_delete(self, ctx, *, tag_name: str):
        """
        Delete a bot tag.
        """
        try:
            tag_name = tag_name.lower()
            self.tags[str(ctx.guild.id)].pop(tag_name)
            tc.update_servers(self.tags)
            tc.save_data()
            await ctx.send(f"Deleted tag `{tag_name}`.")
        except KeyError:
            await ctx.send("Invalid tag!")

    @commands.command(name="taglist", aliases=["listtags", "tags"])
    @commands.cooldown(1, 3)
    @commands.guild_only()
    async def tag_list(self, ctx):
        """
        List available tags for the server.
        """
        guild_tags = self.tags[str(ctx.guild.id)]

        tags = f"{ctx.guild.name} Server Tags\n\n"
        for t in sorted(guild_tags):
            tags += f"[{t}] {guild_tags[str(t)]}\n"

        parts = [(tags[i:i + 750]) for i in range(0, len(tags), 750)]
        for part in parts:
            await ctx.send(f"```{part}```")

    @commands.command()
    @commands.cooldown(1, 3)
    @commands.guild_only()
    async def tag(self, ctx, *, tag_name: str):
        """
        Call a bot tag.
        """

        tag_name = tag_name.lower()

        try:
            response = self.tags[str(ctx.guild.id)][tag_name]

            if response:
                response = self.handle_variables(response, ctx)
                await ctx.send(response)
        except KeyError:
            await ctx.send("Invalid tag!")

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


def setup(bot):
    bot.add_cog(Tags(bot))
