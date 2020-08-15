from discord.ext import commands
import discord

import re
import aiohttp

from util.data.user_data import UserData


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def on_message(self, message):

        emoji_link = "\N{LINK SYMBOL}"

        if not message.guild:
            return

        if not UserData(str(message.guild.id)).booleans.fetch_by_name("aurls_enabled"):
            return

        if message.author == self.bot.user:
            return

        if message.guild:
            mem = message.guild.get_member(message.author.id)
            channel = message.channel
            if mem:
                regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|" \
                        r"(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
                url_list = re.findall(regex, message.content)
                # base_url = "https://tinyurl.com/api-create.php?url={}"

                new_message = message.content
                if len(url_list) > 0:
                    send_message = False
                    for url in url_list:
                        if len(url[0]) > 100:  # Max Length
                            send_message = True
                            shortened = "[URL]({})".format(url[0])
                            new_message = new_message.replace(url[0], shortened)
                            await message.add_reaction(emoji_link)

                    try:
                        wf_react, _ = await self.bot.wait_for('reaction_add', check=(lambda m, u: u.id == message.author.id), timeout=10)
                        wf_react = str(wf_react.emoji)
                    except Exception:
                        await message.clear_reaction(emoji_link)
                        return

                    if send_message and wf_react == emoji_link:
                        embed = discord.Embed(color=0xdd4d28)
                        embed.set_author(name=message.author, icon_url=message.author.avatar_url)
                        embed.description = new_message
                        embed.timestamp = message.created_at
                        embed.set_footer(text="URLs were automatically shortened.")

                        await channel.send(embed=embed)
                        await message.delete()

    @commands.command(name="toggleaurls", aliases=["toggleautourlshorten"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    async def toggle_aurls(self, ctx):
        """
        Toggle the Semi-Auto URL Shorten

        When enabled, the bot will semi-automatically shorten any long urls.
        """
        result = UserData(str(ctx.guild.id)).booleans.toggle_boolean("aurls_enabled")
        await ctx.send(f'**{"Enabled" if result else "Disabled"}** auto url shortening.')


def setup(bot):
    bot.add_cog(Utility(bot))
