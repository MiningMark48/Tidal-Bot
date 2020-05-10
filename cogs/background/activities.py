import asyncio
import json
import random

import discord
from discord import ActivityType as aT
from discord.ext import commands, tasks


class Background(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        self.index = 0
        self.lock = asyncio.Lock()

        self.activities = {}
        # self.act_iter = None  # For Cycling

    @commands.Cog.listener("on_ready")
    async def on_ready(self):
        config_path = "config.json"
        types = {
            "p": aT.playing,
            "w": aT.watching,
            "s": aT.streaming,
            "l": aT.listening
        }
        with open(config_path, 'r') as file:
            data = json.load(file)
            j_act = data["activities"]
            if not j_act:
                self.activities = {"Do !help": aT.playing}
                self.loop.start()
                return
            for item in j_act:
                if j_act[item] in types:
                    self.activities[item] = types[j_act[item]]
                else:
                    self.activities[item] = aT.playing

        # self.act_iter = cycle(self.activities)  # For Cycling
        self.loop.start()

    async def change_activity(self):
        """Bot loop action"""
        # activity = next(self.act_iter)  # Cycle
        activity = random.choice(list(self.activities.keys()))  # Random
        await self.bot.change_presence(activity=discord.Activity(name=activity, type=self.activities.get(activity)))

    @tasks.loop(seconds=5, reconnect=True)
    async def loop(self):
        """Bot loop"""
        async with self.lock:
            await self.change_activity()
            self.index += 1


def setup(bot):
    bot.add_cog(Background(bot))
