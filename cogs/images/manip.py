from io import BytesIO

import discord
import requests
from PIL import Image, UnidentifiedImageError, ImageOps, ImageFilter
from discord.ext import commands


class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="imgrayscale", aliases=["imgs"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def grayscale(self, ctx, url=None):
        """
        Image Manipulation: Grayscale
        """

        if not url:
            url = ctx.author.avatar_url

        try:
            r = requests.get(url, timeout=2)
            buffer = BytesIO(r.content)

            async with ctx.typing():
                with Image.open(buffer) as im:
                    im = im.convert("LA")

                    final_buffer = BytesIO()
                    im.save(final_buffer, "png")

                final_buffer.seek(0)
                file = discord.File(filename=f"manipulated_image.png", fp=final_buffer)
                await ctx.send(file=file)

        except UnidentifiedImageError:
            await ctx.send("Invalid URL!")
            return

    @commands.command(name="imsepia", aliases=["ims"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def sepia(self, ctx, url=None):
        """
        Image Manipulation: Sepia
        """

        if not url:
            url = ctx.author.avatar_url

        try:
            r = requests.get(url, timeout=2)
            buffer = BytesIO(r.content)

            async with ctx.typing():
                with Image.open(buffer) as im:
                    im = im.convert("RGB")
                    width, height = im.size

                    pixels = im.load()

                    for py in range(height):
                        for px in range(width):
                            r, g, b = im.getpixel((px, py))

                            tr = min(int(0.393 * r + 0.769 * g + 0.189 * b), 255)
                            tg = min(int(0.349 * r + 0.686 * g + 0.168 * b), 255)
                            tb = min(int(0.272 * r + 0.534 * g + 0.131 * b), 255)

                            pixels[px, py] = (tr, tg, tb)

                    final_buffer = BytesIO()
                    im.save(final_buffer, "png")

                final_buffer.seek(0)
                file = discord.File(filename=f"manipulated_image.png", fp=final_buffer)
                await ctx.send(file=file)

        except UnidentifiedImageError:
            await ctx.send("Invalid URL!")
            return

    @commands.command(name="imblur", aliases=["imb"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def blur(self, ctx, url=None, radius=5):
        """
        Image Manipulation: Blur
        """

        if not url:
            url = ctx.author.avatar_url

        try:
            r = requests.get(url, timeout=2)
            buffer = BytesIO(r.content)

            async with ctx.typing():
                with Image.open(buffer) as im:
                    im = im.convert("RGB")

                    im = im.filter(ImageFilter.GaussianBlur(radius=radius))

                    final_buffer = BytesIO()
                    im.save(final_buffer, "png")

                final_buffer.seek(0)
                file = discord.File(filename=f"manipulated_image.png", fp=final_buffer)
                await ctx.send(file=file)

        except UnidentifiedImageError:
            await ctx.send("Invalid URL!")
            return


def setup(bot):
    bot.add_cog(Images(bot))
