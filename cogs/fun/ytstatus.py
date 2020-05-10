import re

from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_member_update")
    async def on_member_update(self, before, after):
        base_url = "https://www.youtube.com/watch?v="
        users = [138819223932633088, 138825320831778816, 136130217537306624]
        if after.id in users and before.guild.id == 138819614275665920:
            if before.activity is not None and before.activity != after.activity:
                activity = str(after.activity)
                activity = re.sub(r"<.+>", "", activity)
                activity = activity.replace(" ", "")
                if len(activity) == 11:
                    channel = self.bot.get_channel(661842427035779073)
                    yt_url = f"{base_url}{activity}"
                    await channel.send(f"{after}'s YouTube Status:\n{yt_url}")


def setup(bot):
    bot.add_cog(Fun(bot))
