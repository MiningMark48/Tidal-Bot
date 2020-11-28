import copy

from discord.ext import commands
from discord.utils import escape_markdown
from fuzzywuzzy import process as fwp

from util.data.guild_data import GuildData


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="customcommand", aliases=["customcmd"])
    @commands.cooldown(1, 2)
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def custom_commands(self, ctx):
        """
        Manage custom commands for the server.
        """

        if ctx.invoked_subcommand is None:
            await ctx.send(f"Invalid subcommand! ")

            msg = copy.copy(ctx.message)
            msg.content = f"{ctx.prefix}help {ctx.command}"
            new_ctx = await self.bot.get_context(msg, cls=type(ctx))
            await self.bot.invoke(new_ctx)

    @custom_commands.command(name="set", aliases=["add"])
    @commands.cooldown(1, 2)
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def custom_set(self, ctx, cmd_name: str, *, cmd: str):
        """
        Set a custom command.
        """

        cmd_name = cmd_name.lower()
        cmd = cmd[:1900]

        GuildData(str(ctx.guild.id)).custom_commands.set(cmd_name, cmd)

        await ctx.send(f"Set custom command `{cmd_name}` to `{escape_markdown(cmd)}`.")

    @custom_commands.command(name="delete", aliases=["remove"])
    @commands.cooldown(1, 2)
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def custom_delete(self, ctx, cmd_name: str):
        """
        Delete a custom command.
        """

        cmd_name = cmd_name.lower()

        result = GuildData(str(ctx.guild.id)).custom_commands.delete(cmd_name)
        if result:
            await ctx.send(f"Deleted custom command `{cmd_name}`.")
        else:
            await ctx.send("Invalid custom command!")

    @custom_commands.command(name="list", aliases=["cmds"])
    @commands.cooldown(1, 2)
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def custom_list(self, ctx):
        """
        List all custom commands.
        """

        guild_cmds = GuildData(str(ctx.guild.id)).custom_commands.fetch_all()

        if not len(guild_cmds) > 0:
            await ctx.send("No tags available!")
            return

        tags = f"{ctx.guild.name} Custom Commands\n\n"
        for t in sorted(guild_cmds):
            value = t[2]
            value = value.replace("\n", "")
            tags += f"[{t[1]}] {escape_markdown(value[:100])}{'...' if len(value) > 100 else ''}\n"

        parts = [(tags[i:i + 750]) for i in range(0, len(tags), 750)]
        for part in parts:
            part = part.replace("```", "")
            await ctx.send(f"```{part}```")

    # @commands.command(name="tagvariables", aliases=["tagvars", "variables", "vars"])
    # @commands.cooldown(1, 3)
    # @commands.guild_only()
    # async def tag_variables(self, ctx):
    #     """
    #     Get the list of supported tag variables.
    #
    #     Tag variables are parts of a string that get replace by specific data.
    #     """
    #
    #     variables = self.get_variables(ctx)
    #
    #     vs = f"Tag Variables\n\n"
    #     for v in sorted(variables):
    #         vs += f"[{v}] Ex: {variables[str(v)]}\n"
    #
    #     parts = [(vs[i:i + 750]) for i in range(0, len(vs), 750)]
    #     for part in parts:
    #         await ctx.send(f"```{part}```")
    #
    # @staticmethod
    # def get_variables(ctx):
    #     variables = {
    #         "author": ctx.author.display_name,
    #         "author_id": ctx.author.id,
    #         "channel": ctx.channel.name,
    #         "command_key": ctx.prefix,
    #         "server_id": ctx.guild.id,
    #         "server_name": ctx.guild.name
    #     }
    #
    #     return variables
    #
    # def handle_variables(self, message, ctx):
    #     variables = self.get_variables(ctx)
    #
    #     def to_key(v_):
    #         return f"${{{v_}}}"
    #
    #     for v in variables:
    #         message = message.replace(to_key(v), str(variables[v]))
    #
    #     return message
    #
    # @staticmethod
    # def handle_search(ctx, tag_name):
    #     options = []
    #     for tag in GuildData(str(ctx.guild.id)).tags.fetch_all():
    #         options.append(tag[1])
    #
    #     search_results = fwp.extract(tag_name, options)
    #
    #     return search_results

    @commands.Cog.listener("on_message")
    async def on_message(self, payload):

        if payload.author == self.bot.user:
            return

        ctx = await self.bot.get_context(payload)
        if ctx:
            if ctx.guild and ctx.prefix:
                if str(payload.content).startswith(ctx.prefix * 2):  # Checks if prefix is twice iterated (! -> !!)
                    cmd = str(payload.content).replace(ctx.prefix * 2, "").split(" ")[0]
                    cstm_cmd = GuildData(str(ctx.guild.id)).custom_commands.fetch_by_name(cmd)
                    if cstm_cmd:
                        await ctx.send(cstm_cmd)
                        print(cstm_cmd)


def setup(bot):
    bot.add_cog(Utility(bot))
