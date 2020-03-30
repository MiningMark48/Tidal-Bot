from io import BytesIO

import discord
from PIL import Image
from discord.ext import commands


class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mfractal", aliases=["fractal", "mf"])
    @commands.cooldown(2, 30, commands.BucketType.user)
    async def m_fractal(self, ctx):
        """Create a Mandelbrot Fractal"""

        async with ctx.typing():
            xa = -2.0
            xb = 1.0
            ya = -1.5
            yb = 1.5
            maxIt = 64  # iterations
            # image size
            imgx = 512
            imgy = 512
            with Image.new("RGB", (imgx, imgy)) as image:
                for y in range(imgy):
                    cy = y * (yb - ya) / (imgy - 1) + ya
                    for x in range(imgx):
                        cx = x * (xb - xa) / (imgx - 1) + xa
                        c = complex(cx, cy)
                        z = 0
                        for i in range(maxIt):
                            if abs(z) > 2.0:
                                break
                            z = z * z + c
                        r = i % 4 * 64
                        g = i % 8 * 32
                        b = i % 16 * 16
                        image.putpixel((x, y), b * 65536 + g * 256 + r)

                final_buffer = BytesIO()
                image.save(final_buffer, "png")

                final_buffer.seek(0)
                file = discord.File(filename=f"mandelbrot_fractal.png", fp=final_buffer)
                await ctx.send(file=file)


def setup(bot):
    bot.add_cog(Images(bot))
