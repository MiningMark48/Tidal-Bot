![Tidal Bot](.README_images/banner.png)

![MIT License](https://img.shields.io/github/license/MiningMark48/Tidal-Bot)
[![Discord](https://img.shields.io/discord/138819614275665920?label=Discord&logo=Discord&style=social)](https://discord.gg/SMCEXw5)
[![Twitter](https://img.shields.io/twitter/follow/miningmark48?style=social)](https://twitter.com/miningmark48)

<!-- [![Tidal Wave](https://discord.com/api/guilds/138819614275665920/embed.png)](https://discord.gg/SMCEXw5) -->


 Tidal Bot is a personal bot for [Discord](https://discord.com) written in Python using [discord.py](https://github.com/Rapptz/discord.py) that serves the needs of the [Tidal Waves](https://discord.gg/SMCEXw5). Currently, Tidal Bot is private and added to select servers. I hope to change this in the near future.
 
 For Tidal Bot's predecessor written in Java, see [Tidal-Bot-Java](https://github.com/MiningMark48/Tidal-Bot-Java).

 ## Features

 Tidal Bot has an ever-expanding list of features that include:
 - Server Management
 - Fun
 - Memes
 - Information
 - Utility
 - Bot Management
 - Admin/Bot Owner
 - [Custom Commands](https://github.com/MiningMark48/Tidal-Bot/wiki/Custom-Commands)
 - Music (Requires local [Lavalink](https://github.com/Frederikam/Lavalink) server)
 - Background Features:
   - Quoting
     - Add a webhook named *tb-quote* and react with 📌 (pushpin)
   - "R U Mobile?" - Mobile message detection
     - Use the *rum* command to enable
 - and more!

For a list of all available commands, see [commands.md](https://github.com/MiningMark48/Tidal-Bot/blob/master/commands.md).

<!-- or, for a JSON format, [commands.json](https://github.com/MiningMark48/Tidal-Bot/blob/master/commands.json). -->

If desired, extensions (or "cogs") can be enabled/disabled in the [extensions.toml](https://github.com/MiningMark48/Tidal-Bot/blob/master/extensions.toml) file.

----------

## Issues

If you encounter any issues or have feedback while using the bot, please report them to the [issue tracker](https://github.com/MiningMark48/Tidal-Bot/issues) or by using the *feedback* command: `!feedback <query>`. The feedback command will report your query to a channel in the [Tidal Wave Discord](https://discord.gg/SMCEXw5).


## Running
Although **not intended or supported yet**, do the following to run Tidal Bot yourself:

1. Ensure you have [Python 3.7](https://www.python.org/downloads/) or higher installed
2. Create a [virtual environment](https://docs.python-guide.org/dev/virtualenvs/)
   - `python3.7 -m venv venv`
3. Activate the virtual environment
   - Windows: `.\venv\Scripts\activate` or `activate venv`
4. Install dependencies found in [requirements.txt](https://github.com/MiningMark48/Tidal-Bot/blob/master/requirements.txt)
   - `pip install -r requirements.txt`
5. Create a *config.toml*
   - See [demo_config.toml](https://github.com/MiningMark48/Tidal-Bot/blob/master/demo_config.toml) for a demo config file
6. Run *<span>bot.py</span>*
   - `python bot.py` 

Report issues to the [issue tracker](https://github.com/MiningMark48/Tidal-Bot/issues).

**Note:** As previously mentioned, running the bot yourself is not *fully* supported. This means you may encounter issues. If you report issues to the tracker regarding you running it yourself, please make that known.

### Data Storage
Data is managed using [SQLAlchemy](https://www.sqlalchemy.org/) with the creation of databases. These databases are stored in the `/data` directory. All databases are backed up upon running the bot into the `/backups` directory with zip files for each day.

If a [*b2.toml*](https://github.com/MiningMark48/Tidal-Bot/blob/master/demo_b2.toml) file is supplied **and** if enabled in the config, backups will be automatically uploaded to a remote [Backblaze B2 Cloud Server](https://www.backblaze.com/b2/cloud-storage.html). Upload will be skipped if file is missing or if it's disabled in the config.

-------------

## Miscellaneous Info

### Contributions
Special thanks to the following people and all others who have contributed to the project.
- [Zetor777](https://twitter.com/Zetor777)
- [kaosjr](https://twitter.com/daKaosjr)

### Links
Here are some potentially relevant links.
- [Tidal Wave Discord](https://discord.gg/SMCEXw5) 
- [Tidal Bot ClickUp](https://share.clickup.com/b/h/4-12633923-2/c9aa38f4ceedf1c) (Previously Trello)

----------

## Legal

### License
Tidal Bot uses the [MIT License](https://github.com/MiningMark48/Tidal-Bot/blob/master/LICENSE). 

### Disclaimer
Tidal Bot is not affiliated with [Discord](https://discord.com) or [discord.py](https://github.com/Rapptz/discord.py). 

Although severity is unlikely, I, MiningMark48, am not responsible for what may occur if you decide to run this bot yourself or if the bot is added to your server.

----------
