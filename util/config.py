import os.path as osp
import toml

from util.logger import Logger


class BotConfig:

    def __init__(self):
        self.config_path = "config.toml"
        self.def_config = {
            'bot': {
                'token': 'bot.token', 'key': '!', 'owners': []
            },
            'music': {
                'enabled': False,
                'whitelist_servers': []
            },
            'api_keys': {
                'api': 'key'
            },
            'misc': {
                'feedback_channel': 12341234123412,
                'create_commands_list': True,
                'b2_backups': False
            }
        }

        self.data = self.load_data()
        self.do_run = True

    def load_data(self):
        if osp.isfile(self.config_path):
            with open(self.config_path, 'r') as file:
                data = toml.load(file)
                # Logger.info("Config loaded.")
                return data

        else:
            with open(self.config_path, 'w') as file:
                Logger.warn("Config file not found, creating...")
                toml.dump(self.def_config, file)
                Logger.success("Config file created")
                self.do_run = False
                raise Exception("Config created, needs to be filled.")

    def get_api_key(self, name):
        try:
            result = self.data['api_keys'][name]
            if result:
                return result
        except KeyError:
            Logger.fatal(f"API key not found : {name}")
            return None
