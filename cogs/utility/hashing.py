import aiohttp
import hashlib
import copy

import discord
from discord.ext import commands
from discord import Color


class Hashing:

	def hash(self, string):
		hashed = hashlib.md5(string.encode())
		return hashed.hexdigest()

	def check_hash(self, string, md_hash):
		hashed = self.hash(string)
		return hashed == md_hash


class Utility(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.hashing = Hashing()

	@commands.group(aliases=["hashing"])
	@commands.cooldown(2, 5)
	async def hash(self, ctx):
		"""Commands that related to hashing strings to MD5"""

		if ctx.invoked_subcommand is None:
			await ctx.send(f"Invalid subcommand! ")

			msg = copy.copy(ctx.message)
			msg.content = f"{ctx.prefix}help {ctx.command}"
			new_ctx = await self.bot.get_context(msg, cls=type(ctx))
			await self.bot.invoke(new_ctx)

	@hash.command(name="create", aliases=["generate"])
	async def hash_create(self, ctx, *, text: str):
		"""Hash text to MD5"""

		hashed = self.hashing.hash(text)

		embed = discord.Embed(title="MD5 Hash", color=Color.dark_theme())
		embed.add_field(name="Original", value=text, inline=False)
		embed.add_field(name="Hashed", value=hashed, inline=False)

		await ctx.send(embed=embed)

	@hash.command(name="check", aliases=["match", "matches"])
	async def hash_check(self, ctx, hashed: str, *, text: str):
		"""Check to see if a MD5 hash matches text"""

		hash_match = self.hashing.check_hash(text, hashed)

		embed = discord.Embed(title="MD5 Hash: Check", color=Color.dark_theme())
		embed.add_field(name="Text", value=text, inline=False)
		embed.add_field(name="Hash", value=hashed, inline=False)
		embed.add_field(name="Matches?", value=f"{'Yes' if hash_match else 'No'}", inline=False)

		await ctx.send(embed=embed)


def setup(bot):
	bot.add_cog(Utility(bot))
