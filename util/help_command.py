from discord.ext import commands


class HelpCommand(commands.MinimalHelpCommand):

    def __init__(self):
        super().__init__(
            dm_help=True,
            paginator=commands.Paginator()
        )

    def get_opening_note(self):
        return None

    def get_ending_note(self):
        command_name = self.invoked_with
        return "Type {0}{1} <command> for more info on a command.".format(self.clean_prefix, command_name)

    async def send_cog_help(self, cog):
        """Disabled"""
        pass

    def add_bot_commands_formatting(self, cmds, heading):
        if cmds:
            joined = '  '.join(c.name for c in cmds)
            self.paginator.add_line(f"[{heading}]")
            self.paginator.add_line(f"\t{joined}\n")

    def add_aliases_formatting(self, aliases):
        self.paginator.add_line('\n%s %s' % (self.aliases_heading, ', '.join(aliases)), empty=True)
