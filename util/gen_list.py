import json

from PIL import ImageFont, ImageDraw, Image

from util.logger import Logger


class Generator:
    """
    Generator class for saving all commands to a list.
    """

    def __init__(self, bot):
        """
        :param bot: Discord Bot client
        """

        self.bot = bot
        self.commands = self.bot.commands

    def fetch_list(self):
        """
        Compiles bot commands into a single list containing:
        name, aliases, type, usage, action, and hidden status

        :return: list
        """

        cmds_list = []
        for cmd in self.commands:
            cmd_o = {
                "name": str(cmd.name),
                "aliases": ", ".join(cmd.aliases),
                "type": str(cmd.cog_name),
                "usage": "--",
                "action": str(cmd.help),
                "hidden": cmd.hidden
            }
            cmds_list.append(cmd_o)

        return sorted(cmds_list, key=lambda i: (i['name'], i['aliases'], i['type'], i['action'], i['usage']))
        # return sorted(cmds_list, key=lambda i: (i['type'], i['name'], i['aliases'], i['action'], i['usage']))

    def gen_list(self):
        """
        Generates a list of all commands to a JSON file (`commands.json`)

        Useful for a data representation of commands for manipulation.
        """

        path = "commands.json"
        with open(path, 'w') as file:
            cmds = self.fetch_list()
            json.dump(cmds, file, indent=4)
            Logger.info(
                f"Commands list generated at {path} containing {len(cmds)} commands")

    def gen_md_list(self):
        """
        Generates a list of all commands to a markdown file (`commands.md`)

        Useful for a visual representation of commands.
        """

        path = "commands.md"
        with open(path, 'w') as file:
            all_cmds = self.fetch_list()
            # Filter out hidden commands
            cmds = list(filter(lambda c: not c['hidden'], all_cmds))

            header = "# Commands\n" \
                     "**Commands Available:** {0}\n" \
                     "| Name    | Description | Category | Aliases |\n" \
                     "|---------|-------------|----------|---------|"

            header = header.format(len(cmds))

            content = f"{header}\n"
            for cmd in cmds:
                cmd_name = str(cmd['name']).replace("|", "")
                cmd_desc = str(cmd['action']).replace(
                    "|", "").replace("\n", " ")
                cmd_cat = str(cmd['type']).replace("|", "")
                cmd_alia = str(cmd['aliases']).replace(
                    "|", "") if cmd['aliases'] else "N/A"
                content += f"| {cmd_name} | {cmd_desc} | {cmd_cat} | {cmd_alia} |\n"

            content += f"\n*Plus {(len(all_cmds) - len(cmds))} hidden.*\n\nThis file was automatically generated."

            file.write(content)
            Logger.info(
                f"Commands MD list generated at {path} containing {len(cmds)} commands")

    def gen_img_list(self):
        """
        Generates a set of images to list all commands.

        Generates to `cmdimgs/commands_#.png`
        """

        def shorten_text(t: str, max_chars: int):
            if len(t) > max_chars:
                return "{}...".format(t[:max_chars])
            return t

        path = "cmdimgs/commands_{}.png"
        cmds = self.fetch_list()

        part_size = 30
        parted_cmds = [(cmds[i:i + part_size])
                       for i in range(0, len(cmds), part_size)]

        i = 1
        for part in parted_cmds:

            with Image.new("RGB", (2200, 2000), 0xffffff) as im:

                draw = ImageDraw.Draw(im)

                text_color = 0x000000

                title_font_size = 70
                title_font = ImageFont.truetype(
                    './resources/fonts/arial.ttf', size=title_font_size)
                title_text = "Commands"

                subtitle_font_size = 65
                subtitle_font = ImageFont.truetype(
                    './resources/fonts/arial.ttf', size=subtitle_font_size)

                norm_font_size = 50
                norm_font = ImageFont.truetype(
                    './resources/fonts/arial.ttf', size=norm_font_size)

                # pylint: disable=unused-variable
                w, h = im.size

                # Title
                title_width = draw.textsize(title_text, title_font)[0]
                draw.text(((w - title_width) / 2, 35), title_text,
                          fill=text_color, font=title_font)

                draw.text((50, 150), "Name", fill=text_color,
                          font=subtitle_font)
                draw.text((650, 150), "Description",
                          fill=text_color, font=subtitle_font)

                start_y = 250
                for cmd in part:
                    desc = cmd['action'].replace("\n", " - ")
                    desc = shorten_text(desc, 55)

                    draw.text((50, start_y),
                              cmd['name'], fill=text_color, font=norm_font)
                    draw.text((650, start_y), desc,
                              fill=text_color, font=norm_font)
                    start_y += 60

                # im = im.crop((0, 0, w, (h / 2) + (shape_h / 2) + spacing))

                # im.resize((1920, 1080))
                im.save(path.format(i), "png")

                i += 1

        Logger.info("Commands list images generated.")
