import aiohttp
import discord
from bs4 import BeautifulSoup as bs
from discord.ext import commands

from util.decorators import delete_original


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.new_game = []

    @commands.command(name="pressbutton", aliases=["wyptb", "pushbutton"])
    @delete_original()
    async def press_button(self, ctx):
        """
        Will you press the button?
        """

        site_url = "http://willyoupressthebutton.com/"

        async with aiohttp.ClientSession() as session:
            async with session.get(site_url) as r:
                content = await r.content.read()

                soup = bs(content, 'html.parser')
                left_div = soup.find_all(id='cond')[0]
                right_div = soup.find_all(id='res')[0]

                left_text = left_div.text
                right_text = right_div.text

                embed = discord.Embed(title="Will you press the button?", color=0x054c8a)
                embed.description = f"{left_text}\n*but*\n{right_text}"
                embed.set_footer(text="Fetched from willyoupressthebutton.com")
                msg = await ctx.send(embed=embed)

                await msg.add_reaction("✅")
                await msg.add_reaction("❎")

                self.new_game.append(msg.id)
                await msg.add_reaction("🔁")

    @commands.Cog.listener("on_raw_reaction_add")
    async def on_raw_reaction_add(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        rmsg = await channel.fetch_message(payload.message_id)

        if rmsg.id in self.new_game:
            reaction_emoji = str(payload.emoji)
            user = self.bot.get_user(payload.user_id)
            if reaction_emoji == '🔁':
                if not user == self.bot.user:
                    ctx = await self.bot.get_context(rmsg)
                    cmd = self.bot.get_command("pressbutton")
                    self.new_game.remove(rmsg.id)
                    await rmsg.clear_reaction("🔁")
                    await ctx.invoke(cmd)


def setup(bot):
    bot.add_cog(Fun(bot))
