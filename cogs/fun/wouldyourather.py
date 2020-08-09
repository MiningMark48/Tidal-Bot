import aiohttp
import discord
from bs4 import BeautifulSoup as bs
from discord.ext import commands

from util.decorators import delete_original


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.new_game = []

    @commands.command(name="wouldyourather", aliases=["wyr", "wouldrather"])
    @delete_original()
    async def would_you_rather(self, ctx):
        """
        Would you rather...?
        """

        site_url = "http://either.io/"

        async with aiohttp.ClientSession() as session:
            async with session.get(site_url) as r:
                content = await r.content.read()

                soup = bs(content, 'html.parser')

                panel_div = soup.find_all("div", class_="panel")[0]

                left_div = panel_div.find_all("div", class_=["choice-block blue-choice",
                                                             "choice-block blue-choice selected"])[0]
                right_div = panel_div.find_all("div", class_=["choice-block red-choice",
                                                              "choice-block red-choice selected"])[0]

                left_text = left_div.find_all("span", class_="option-text")[0].text
                right_text = right_div.find_all("span", class_="option-text")[0].text

                embed = discord.Embed(title="Would you rather...", color=0x88387d)
                embed.description = f"🇦 {left_text}\n\n*or*\n\n🇧 {right_text}?"
                embed.set_footer(text="Fetched from either.io")
                msg = await ctx.send(embed=embed)

                await msg.add_reaction("🇦")
                await msg.add_reaction("🇧")

                self.new_game.append(msg.id)
                await msg.add_reaction("\N{CLOCKWISE RIGHTWARDS AND LEFTWARDS OPEN CIRCLE ARROWS}")

    @commands.Cog.listener("on_raw_reaction_add")
    async def on_raw_reaction_add(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        rmsg = await channel.fetch_message(payload.message_id)

        if rmsg.id in self.new_game:
            reaction_emoji = str(payload.emoji)
            user = self.bot.get_user(payload.user_id)
            if reaction_emoji == '\N{CLOCKWISE RIGHTWARDS AND LEFTWARDS OPEN CIRCLE ARROWS}':
                if not user == self.bot.user:
                    ctx = await self.bot.get_context(rmsg)
                    cmd = self.bot.get_command("wouldyourather")
                    self.new_game.remove(rmsg.id)
                    await rmsg.clear_reaction("\N{CLOCKWISE RIGHTWARDS AND LEFTWARDS OPEN CIRCLE ARROWS}")
                    await ctx.invoke(cmd)


def setup(bot):
    bot.add_cog(Fun(bot))
