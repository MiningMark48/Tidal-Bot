import aiohttp
import random
from functools import partial
from io import BytesIO

import discord
from PIL import Image, ImageDraw, ImageFont
from discord.ext import commands


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=bot.loop)

    @staticmethod
    def processing_color(sq: int):
        sq_w = 250
        with Image.new("RGB", (sq_w*sq, 200), 0xffffff) as im:
            font_text_size = 20
            font_text = ImageFont.truetype(f'./resources/fonts/arial.ttf', size=font_text_size)
            draw = ImageDraw.Draw(im)

            for squ in range(0, sq):
                r, g, b = rgb = c()
                hex_text = str('#%02x%02x%02x' % (r, g, b)).upper()
                font_color = 0x000000 if (r * 0.299 + g * 0.587 + b * 0.114) > 186 else 0xffffff

                hex_start = (25 + sq_w * squ, 10)

                shape = ((sq_w * squ, 0), (sq_w + (sq_w * squ), im.size[1]))
                draw.rectangle(shape, fill=rgb)

                # Borders
                # shape2 = ((sq_w * squ, 0), (sq_w * squ + 5, im.size[1]))
                # draw.rectangle(shape2, fill=0x000000)

                spacing = 25
                draw.text((hex_start[0], hex_start[1]), hex_text, fill=font_color, font=font_text)
                draw.text((hex_start[0], hex_start[1] + spacing), str(rgb), fill=font_color, font=font_text)

            final_buffer = BytesIO()
            im.save(final_buffer, "png")

        final_buffer.seek(0)
        return final_buffer

    @commands.command(name="colorgen", aliases=["gencolor", "randcolor"])
    @commands.cooldown(3, 5, commands.BucketType.user)
    async def color_gen(self, ctx, squares=1):
        """
        Generate a random color or palette of colors

        Squares amount: min=1, max=5
        """
        squares = max(min(squares, 5), 1)

        async with ctx.typing():
            fn = partial(self.processing_color, squares)
            final_buffer = await self.bot.loop.run_in_executor(None, fn)
            file = discord.File(filename="color_gen.png", fp=final_buffer)
            await ctx.send(file=file)


def c():
    col = []
    for i in range(0, 3):
        col.append(random.randint(0, 255))
    return tuple(col)


# def hilo(a, b, c):
#     if c < b: b, c = c, b
#     if b < a: a, b = b, a
#     if c < b: b, c = c, b
#     return a + c
#
#
# def complement(r, g, b):
#     k = hilo(r, g, b)
#     return tuple(k - u for u in (r, g, b))


def setup(bot):
    bot.add_cog(Utility(bot))
