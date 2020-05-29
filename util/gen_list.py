import json

from util.logger import Logger


class Generator:
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.commands

    def fetch_list(self):
        cmds_list = []
        for cmd in self.commands:
            cmd_o = {
                "name": str(cmd.name),
                "aliases": ", ".join(cmd.aliases),
                "type": str(cmd.cog_name),
                "usage": "--",
                "action": str(cmd.help)
            }
            cmds_list.append(cmd_o)

        return sorted(cmds_list, key=lambda i: (i['name'], i['aliases'], i['type'], i['action'], i['usage']))
        # return sorted(cmds_list, key=lambda i: (i['type'], i['name'], i['aliases'], i['action'], i['usage']))

    def gen_list(self):
        path = "commands.json"
        with open(path, 'w') as file:
            cmds = self.fetch_list()
            json.dump(cmds, file, indent=4)
            Logger.info(f"Commands list generated at {path} containing {len(cmds)} commands")
