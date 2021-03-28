from discord.ext import commands, ipc

from util.data.guild_data import GuildData


class IPCRoutes(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@ipc.server.route()
	async def cmd_say(self, data):
		channel = self.bot.get_guild(int(data.guild_id)).get_channel(int(data.channel_id))
		await channel.send(data.message)

	@ipc.server.route()
	async def set_prefix(self, data):
		GuildData(str(data.guild_id)).strings.set("prefix", str(data.prefix))

	@ipc.server.route()
	async def set_nickname(self, data):
		await self.bot.get_guild(int(data.guild_id)).get_member(self.bot.user.id).edit(nick=data.nickname)

	@ipc.server.route()
	async def set_join_msg(self, data):
		GuildData(str(data.guild_id)).strings.set("join_message", data.message)

	@ipc.server.route()
	async def get_join_msg(self, data):
		msg = GuildData(str(data.guild_id)).strings.fetch_by_name("join_message")
		print(msg)
		return msg

def setup(bot):
	bot.add_cog(IPCRoutes(bot))
