import asyncio
from datetime import datetime as dt
from io import BytesIO

import discord
from PIL import Image
from discord.ext import commands, tasks


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.index = 0
        self.lock = asyncio.Lock()
        self.loop.start()

    async def do_mccree(self):
        """Bot loop action"""
        time = dt.now()
        if time.minute == 0:
            channel = discord.utils.find(
                lambda c: (isinstance(c, discord.TextChannel) and "[tb-mccree]" in (c.topic if c.topic else "")),
                self.bot.get_all_channels())
            if channel:
                with Image.open("./memetemps/highnoon.png") as im:
                    final_buffer = BytesIO()
                    im.save(final_buffer, "png")
                final_buffer.seek(0)

                file = discord.File(filename=f"highnoon.png", fp=final_buffer)

                await channel.send(file=file)

    @tasks.loop(minutes=1, reconnect=True)
    async def loop(self):
        """Bot loop"""
        async with self.lock:
            await self.do_mccree()
            self.index += 1


def setup(bot):
    bot.add_cog(Fun(bot))
