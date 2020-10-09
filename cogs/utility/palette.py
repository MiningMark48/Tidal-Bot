import random

import aiohttp
import discord
from PIL import ImageFilter, Image, UnidentifiedImageError, ImageFont, ImageDraw, ImageOps
from discord.ext import commands
from io import BytesIO


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.session = aiohttp.ClientSession(loop=bot.loop)

    # @staticmethod
    # def processing_color(sq: int):
    #     sq_w = 250
    #     with Image.new("RGB", (sq_w*sq, 200), 0xffffff) as im:
    #         font_text_size = 20
    #         font_text = ImageFont.truetype(f'./resources/fonts/arial.ttf', size=font_text_size)
    #         draw = ImageDraw.Draw(im)
    #
    #         for squ in range(0, sq):
    #             r, g, b = rgb = c()
    #             hex_text = str('#%02x%02x%02x' % (r, g, b)).upper()
    #             font_color = 0x000000 if (r * 0.299 + g * 0.587 + b * 0.114) > 186 else 0xffffff
    #
    #             hex_start = (25 + sq_w * squ, 10)
    #
    #             shape = ((sq_w * squ, 0), (sq_w + (sq_w * squ), im.size[1]))
    #             draw.rectangle(shape, fill=rgb)
    #
    #             # Borders
    #             # shape2 = ((sq_w * squ, 0), (sq_w * squ + 5, im.size[1]))
    #             # draw.rectangle(shape2, fill=0x000000)
    #
    #             spacing = 25
    #             draw.text((hex_start[0], hex_start[1]), hex_text, fill=font_color, font=font_text)
    #             draw.text((hex_start[0], hex_start[1] + spacing), str(rgb), fill=font_color, font=font_text)
    #
    #         final_buffer = BytesIO()
    #         im.save(final_buffer, "png")
    #
    #     final_buffer.seek(0)
    #     return final_buffer

    @commands.command(aliases=["colpal"])
    @commands.cooldown(3, 5, commands.BucketType.user)
    async def palette(self, ctx, url: str, top=False):
        """
        Get a random color palette from an image.

        If 'Top' is true, command will grab the
        most used colors instead of random.
        """

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as r:
                    content = await r.content.read()
                    buffer = BytesIO(content)

            async with ctx.typing():
                with Image.open(buffer) as im:
                    im = im.convert("RGB")

                    if not top:
                        colors = sorted(im.getcolors(maxcolors=im.size[0] * im.size[1]), reverse=True)
                        palette = [random.choice(colors)[1] for _ in range(0, 5)]
                    else:
                        colors = sorted(im.getcolors(maxcolors=im.size[0] * im.size[1]), reverse=True)[:5]
                        palette = [col[1] for col in colors]

                    sq_w = 150
                    offset = 10
                    with Image.new("RGB", (1920, (sq_w * len(palette) + offset)), 0xffffff) as img:
                        font_text_size = 40
                        font_text = ImageFont.truetype(f'./resources/fonts/arial.ttf', size=font_text_size)
                        font_color = 0x000000
                        draw = ImageDraw.Draw(img)

                        i = 0
                        for col in palette:
                            shape = ((offset, sq_w * i + offset), (sq_w, sq_w + (sq_w * i)))
                            draw.rectangle(shape, fill=col)

                            hex_start = ((offset + sq_w), (sq_w * i + offset))
                            hex_text = str('#%02x%02x%02x' % (col[0], col[1], col[2])).upper()
                            draw.text((hex_start[0], hex_start[1]), hex_text, fill=font_color, font=font_text)
                            draw.text((hex_start[0], hex_start[1] + font_text_size + offset), str(col), fill=font_color, font=font_text)

                            i += 1

                        img_loc = (round(sq_w * 3.5), offset)
                        base_width = img.size[0] - img_loc[0] - offset

                        if im.size[0] > img.size[0] or im.size[1] > im.size[1]:
                            im.thumbnail((base_width, img.size[1] - (offset * 2)), Image.ANTIALIAS)
                        else:
                            im = ImageOps.fit(im, (base_width, img.size[1] - (offset * 2)), Image.ANTIALIAS)
                        img.paste(im, img_loc)

                    final_buffer = BytesIO()
                    img.save(final_buffer, "png")

                final_buffer.seek(0)
                file = discord.File(filename=f"palette.png", fp=final_buffer)
                await ctx.send(file=file)

        except UnidentifiedImageError:
            await ctx.send("Invalid URL!")
            return


def setup(bot):
    bot.add_cog(Utility(bot))
