import copy
import random
import re

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

    @custom_commands.command(name="variablehelp", aliases=["varhelp", "variables"], hidden=True)
    @commands.cooldown(3, 2)
    @commands.guild_only()
    async def variable_help(self, ctx):
        """
        Get help for how to use custom command variables.
        """

        # TODO: Write documentation and unhide when complete

        url = "TODO"
        await ctx.send(f"{ctx.author.mention}, for help, go here: <{url}>")

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
                        parsed_command = self.parse_variables(ctx, cstm_cmd)
                        await ctx.send(parsed_command)
                        print(cmd, parsed_command)

    def parse_variables(self, ctx, command: str):

        def to_key(v_):
            return f"${{{v_}}}"

        variables = self.get_variables(ctx)
        # print(variables)
        for var in variables:
            command = command.replace(to_key(var), str(variables[var]))

        try:
            command = self.parse_random_num(command)
            command = self.parse_random_list(command)
        except Exception as e:
            command = f"ERROR | {e}"

        return command

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

    @staticmethod
    def parse_random_num(command):
        pattern = r"\${(rand:)(\S*[0-9])\-(\S*[0-9])}"
        r = re.compile(pattern)

        for _, _min, _max in r.findall(command):
            rand_num = str(random.randint(int(_min), int(_max)))
            command = r.sub(rand_num, command, 1)

        return command

    @staticmethod
    def parse_random_list(command):
        pattern = r"\${(randlist:)(\S*[\w])}"
        r = re.compile(pattern)

        for _, rand_list in r.findall(command):
            rand_item = random.choice(rand_list.split("|")).replace("_", " ")
            command = r.sub(rand_item, command, 1)

        return command


def setup(bot):
    bot.add_cog(Utility(bot))
