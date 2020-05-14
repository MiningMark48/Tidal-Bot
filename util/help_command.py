from discord.ext import commands


class HelpCommand(commands.MinimalHelpCommand):

    def __init__(self):
        super().__init__(
            dm_help_threshold=750,
            dm_help=None,
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

    # noinspection PyNoneFunctionAssignment
    async def send_group_help(self, group):
        self.add_command_formatting(group)

        filtered = await self.filter_commands(group.commands, sort=self.sort_commands)
        if filtered:
            note = self.get_opening_note()
            if note:
                self.paginator.add_line(note, empty=True)

            self.paginator.add_line(self.commands_heading)
            for command in filtered:
                self.add_subcommand_formatting(command)

            note = self.get_ending_note()
            if note:
                self.paginator.add_line()
                self.paginator.add_line(note)

        await self.send_pages()
