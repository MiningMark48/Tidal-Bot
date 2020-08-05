from discord.ext import commands

import re
import aiohttp

from util.data.user_data import UserData


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def on_message(self, message):

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
                base_url = "https://tinyurl.com/api-create.php?url={}"

                new_message = f"**{message.author.mention}:**\n\n{message.content}"
                if len(url_list) > 0:
                    for url in url_list:
                        if len(url[0]) > 100:
                            async with aiohttp.ClientSession() as session:
                                async with session.get(base_url.format(url[0])) as r:
                                    content = await r.text()
                                    shortened = str(content)

                                    new_message = new_message.replace(url[0], shortened)

                    await channel.send(new_message)
                    await message.delete()

    @commands.command(name="toggleaurls", aliases=["toggleautourlshorten"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    async def toggle_aurls(self, ctx):
        """
        Toggle the Auto URL Shorten

        When enabled, the bot will automatically shorten any long urls.
        """
        result = UserData(str(ctx.guild.id)).booleans.toggle_boolean("aurls_enabled")
        await ctx.send(f'**{"Enabled" if result else "Disabled"}** auto url shortening.')


def setup(bot):
    bot.add_cog(Utility(bot))
