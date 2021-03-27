import copy
import typing
from contextlib import redirect_stdout

import discord
from discord import channel
from discord.ext import commands, ipc

from util.data.data_backup import backup_databases
from util.logger import Logger


class IPCRoutes(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@ipc.server.route()
	async def get_guild_ids(self, data):
		final = []
		for guild in self.bot.guilds:
			final.append(guild.id)
		return final # returns the guild ids to the client

	@ipc.server.route()
	async def get_guild_count(self, data):
		return len(self.bot.guilds) # returns the len of the guilds to the client

	@ipc.server.route()
	async def get_guild_text_channels(self, data):
		text_channels = self.bot.get_guild(int(data.guild_id)).text_channels
		return [{"name": c.name, "id": c.id} for c in text_channels]

	@ipc.server.route()
	async def cmd_say(self, data):
		channel = self.bot.get_guild(int(data.guild_id)).get_channel(int(data.channel_id))
		await channel.send(data.message)

def setup(bot):
	bot.add_cog(IPCRoutes(bot))
