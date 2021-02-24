import typing

import discord
from discord.ext import commands

from util.decorators import delete_original


class Utility(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		# self.thread_emoji = "\N{Spool of Thread}"

	@commands.command(aliases=["spoil", "blackbar", "hide"])
	@commands.cooldown(5, 2, commands.BucketType.user)
	@delete_original()
	async def spoiler(self, ctx, msg_id: typing.Optional[str]):
		"""
		Start a thread based on the last sent message or a message ID.
		"""

		if msg_id:
			try:
				spoiler_msg = await ctx.channel.fetch_message(msg_id)
			except discord.errors.NotFound:
				return await ctx.send("Message not found!")
		else:
			try:
				msgs = await ctx.channel.history(limit=1).flatten()
				spoiler_msg = msgs[0]
			except IndexError:
				spoiler_msg = ctx.message

		msg_content = spoiler_msg.content
		new_content = f"> ||{msg_content}||\n{spoiler_msg.author.mention}"
		await spoiler_msg.delete()
		
		new_msg = await ctx.send(new_content)

		await ctx.author.send(f"Message was made a spoiler.\n{new_msg.jump_url}", delete_after=10)


	# @commands.Cog.listener("on_raw_reaction_add")
	# async def on_raw_reaction_add(self, payload):
	#     reaction_emoji = str(payload.emoji)
	#     user = payload.member
	#     guild = user.guild
	#     channel = guild.get_channel(payload.channel_id)
	#     msg = await channel.fetch_message(payload.message_id)

	#     if user == self.bot.user or isinstance(channel, discord.DMChannel):
	#         return

	#     if reaction_emoji == self.thread_emoji:
	#         ctx = await self.bot.get_context(msg, cls=commands.Context)
	#         await self.thread_start(ctx, payload.message_id)

	#         await msg.remove_reaction(self.thread_emoji, user)


def setup(bot):
	bot.add_cog(Utility(bot))
