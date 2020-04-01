from io import BytesIO

import discord
import requests
from PIL import Image, UnidentifiedImageError
from discord.ext import commands


class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="fakeping")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def fake_ping(self, ctx, url: str):
        """Create a fake ping image"""

        try:
            r = requests.get(url, timeout=2)
            buffer = BytesIO(r.content)

            async with ctx.typing():
                with Image.open(buffer) as im:
                    im = im.convert("RGBA")

                    im_ping = Image.open("./resources/images/template_ping.png").convert('RGBA')
                    im_ping = im_ping.resize((im.width, im.height))

                    ping_loc = (0, 0)

                    alpha_layer = Image.new('RGBA', im.size, (0, 0, 0, 0))
                    alpha_layer.paste(im_ping, ping_loc)

                    im = Image.alpha_composite(im, alpha_layer)
                    im = im.convert("RGB")

                    final_buffer = BytesIO()
                    im.save(final_buffer, "png")

                final_buffer.seek(0)
                file = discord.File(filename=f"fake_ping.png", fp=final_buffer)
                await ctx.send(file=file)

        except UnidentifiedImageError:
            await ctx.send("Invalid URL!")
            return


def setup(bot):
    bot.add_cog(Images(bot))
