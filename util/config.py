import json
import os.path as osp

from util.logger import Logger


class BotConfig:

    def __init__(self):
        self.config_path = "config.json"
        self.def_config = {
            "bot_token": "!",
            "bot_key": "bot.key",
            "load_music": True,
            "bot_owners": [1234]
        }

        self.data = self.load_data()
        self.do_run = True

    def load_data(self):
        if osp.isfile(self.config_path):
            with open(self.config_path, 'r') as file:
                data = json.load(file)
                Logger.success("Config loaded.")
                return data

        else:
            with open(self.config_path, 'w') as file:
                Logger.warn("Config file not found, creating...")
                json.dump(self.def_config, file, indent=4)
                Logger.success("Config file created.")
                self.do_run = False
                return self.def_config
