import random
from io import BytesIO

import aiohttp
import discord
import requests
from PIL import Image, UnidentifiedImageError, ImageOps, ImageFilter, ImageFont, ImageDraw
from discord.ext import commands


class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="imblur", aliases=["imb"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def blur(self, ctx, url=None, radius=5):
        """
        Image Manipulation: Blur
        """

        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.message.delete()

        if not url:
            url = str(ctx.author.avatar_url)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as r:
                    content = await r.content.read()
                    buffer = BytesIO(content)

            async with ctx.typing():
                with Image.open(buffer) as im:
                    im = im.convert("RGB")

                    im = im.filter(ImageFilter.GaussianBlur(radius=radius))

                    final_buffer = BytesIO()
                    im.save(final_buffer, "png")

                final_buffer.seek(0)
                file = discord.File(filename=f"manipulated_image.png", fp=final_buffer)
                await ctx.send(file=file)

        except (UnidentifiedImageError, requests.exceptions.MissingSchema):
            await ctx.send("Invalid URL!")
            return

    @commands.command(name="imcircle", aliases=["imc"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def circle(self, ctx, url=None):
        """
        Image Manipulation: Circle
        """

        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.message.delete()

        if not url:
            url = str(ctx.author.avatar_url)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as r:
                    content = await r.content.read()
                    buffer = BytesIO(content)

            async with ctx.typing():
                with Image.open(buffer) as im:
                    im = im.convert("RGB")
                    mask = Image.open("./resources/images/template_circle_mask.png").convert('L')
                    mask = mask.resize(im.size)

                    output = ImageOps.fit(im, mask.size, centering=(0.5, 0.5))
                    output.putalpha(mask)
                    # output = output.resize(im.size)

                    final_buffer = BytesIO()
                    output.save(final_buffer, "png")

                final_buffer.seek(0)
                file = discord.File(filename=f"manipulated_image.png", fp=final_buffer)
                await ctx.send(file=file)

        except (UnidentifiedImageError, requests.exceptions.MissingSchema):
            await ctx.send("Invalid URL!")
            return

    @commands.command(name="imflip180", aliases=["imf180"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def flip_180(self, ctx, url=None):
        """
        Image Manipulation: Flip 180
        """

        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.message.delete()

        if not url:
            url = str(ctx.author.avatar_url)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as r:
                    content = await r.content.read()
                    buffer = BytesIO(content)

            async with ctx.typing():
                with Image.open(buffer) as im:
                    im = im.convert("RGB")

                    im = im.rotate(180)

                    final_buffer = BytesIO()
                    im.save(final_buffer, "png")

                final_buffer.seek(0)
                file = discord.File(filename=f"manipulated_image.png", fp=final_buffer)
                await ctx.send(file=file)

        except (UnidentifiedImageError, requests.exceptions.MissingSchema):
            await ctx.send("Invalid URL!")
            return

    @commands.command(name="imgrayscale", aliases=["imgs"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def grayscale(self, ctx, url=None):
        """
        Image Manipulation: Grayscale
        """

        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.message.delete()

        if not url:
            url = str(ctx.author.avatar_url)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as r:
                    content = await r.content.read()
                    buffer = BytesIO(content)

            async with ctx.typing():
                with Image.open(buffer) as im:
                    im = im.convert("LA")

                    final_buffer = BytesIO()
                    im.save(final_buffer, "png")

                final_buffer.seek(0)
                file = discord.File(filename=f"manipulated_image.png", fp=final_buffer)
                await ctx.send(file=file)

        except (UnidentifiedImageError, requests.exceptions.MissingSchema):
            await ctx.send("Invalid URL!")
            return

    @commands.command(name="impixelate", aliases=["imp"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def pixelate(self, ctx, url=None):
        """
        Image Manipulation: Pixelate
        """

        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.message.delete()

        if not url:
            url = str(ctx.author.avatar_url)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as r:
                    content = await r.content.read()
                    buffer = BytesIO(content)

            async with ctx.typing():
                with Image.open(buffer) as im:
                    im = im.convert("RGB")
                    og_size = im.size

                    im = im.resize((32, 32), resample=Image.BILINEAR)
                    im = im.resize(og_size, Image.NEAREST)

                    final_buffer = BytesIO()
                    im.save(final_buffer, "png")

                final_buffer.seek(0)
                file = discord.File(filename=f"manipulated_image.png", fp=final_buffer)
                await ctx.send(file=file)

        except (UnidentifiedImageError, requests.exceptions.MissingSchema):
            await ctx.send("Invalid URL!")
            return

    @commands.command(name="imsepia", aliases=["ims"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def sepia(self, ctx, url=None):
        """
        Image Manipulation: Sepia
        """

        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.message.delete()

        if not url:
            url = str(ctx.author.avatar_url)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as r:
                    content = await r.content.read()
                    buffer = BytesIO(content)

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

        except (UnidentifiedImageError, requests.exceptions.MissingSchema):
            await ctx.send("Invalid URL!")
            return

    @commands.command(name="imsnapchat", aliases=["imsc"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def snapchat(self, ctx, text: str, url=None):
        """
        Image Manipulation: Snapchat
        """

        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.message.delete()

        if not url:
            url = str(ctx.author.avatar_url)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as r:
                    content = await r.content.read()
                    buffer = BytesIO(content)

            async with ctx.typing():
                with Image.open(buffer) as im:
                    im = im.convert("RGBA")

                    width, height = im.size

                    height = random.randint(0, height)
                    scale = 1
                    font_color = 0xffffffff

                    font_size = 24 * scale

                    im_o = Image.new('RGBA', im.size, (0, 0, 0, 0))
                    font = ImageFont.truetype('./resources/fonts/arial.ttf', size=font_size)
                    draw = ImageDraw.Draw(im_o)

                    w, h = im.size
                    tw, th = draw.textsize(text, font)
                    shape_h = 35 * scale
                    shape = ((0, height), (w, height + shape_h))
                    draw.rectangle(shape, fill=(0, 0, 0, 160))

                    draw.text(((w - tw) / 2, height + (shape_h - th) / 2), text, fill=font_color, font=font)

                    im = Image.alpha_composite(im, im_o)
                    im = im.convert("RGB")

                    final_buffer = BytesIO()
                    im.save(final_buffer, "png")

                final_buffer.seek(0)
                file = discord.File(filename=f"manipulated_image.png", fp=final_buffer)
                await ctx.send(file=file)

        except (UnidentifiedImageError, requests.exceptions.MissingSchema):
            await ctx.send("Invalid URL!")
            return


def setup(bot):
    bot.add_cog(Images(bot))
