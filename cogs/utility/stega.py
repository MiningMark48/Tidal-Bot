from io import BytesIO

import aiohttp
import discord
import requests
from PIL import Image, UnidentifiedImageError
from discord.ext import commands

from util.decorators import delete_original


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def gen_data(self, data):

        # list of binary codes
        # of given data
        newd = []

        for i in data:
            newd.append(format(ord(i), '08b'))
        return newd

        # Pixels are modified according to the

    # 8-bit binary data and finally returned
    def mod_pix(self, pix, data):

        datalist = self.gen_data(data)
        lendata = len(datalist)
        imdata = iter(pix)

        for i in range(lendata):

            # Extracting 3 pixels at a time
            pix = [value for value in imdata.__next__()[:3] +
                   imdata.__next__()[:3] +
                   imdata.__next__()[:3]]

            # Pixel value should be made
            # odd for 1 and even for 0
            for j in range(0, 8):
                if (datalist[i][j] == '0') and (pix[j] % 2 != 0):

                    if pix[j] % 2 != 0:
                        pix[j] -= 1

                elif (datalist[i][j] == '1') and (pix[j] % 2 == 0):
                    pix[j] -= 1

            # Eigh^th pixel of every set tells
            # whether to stop ot read further.
            # 0 means keep reading; 1 means the
            # message is over.
            if i == lendata - 1:
                if pix[-1] % 2 == 0:
                    pix[-1] -= 1
            else:
                if pix[-1] % 2 != 0:
                    pix[-1] -= 1

            pix = tuple(pix)
            yield pix[0:3]
            yield pix[3:6]
            yield pix[6:9]

    def encode_enc(self, new_img, data):
        w = new_img.size[0]
        (x, y) = (0, 0)

        for pixel in self.mod_pix(new_img.getdata(), data):

            # Putting modified pixels in the new image
            new_img.putpixel((x, y), pixel)
            if x == w - 1:
                x = 0
                y += 1
            else:
                x += 1

    @commands.group(name="stega", hidden=True)
    @commands.cooldown(1, 3.5)
    async def group_stega(self, ctx):
        """
        Encode and decode an image using Steganography

        Note: Issues may occur.
        """
        pass

    @group_stega.command(name="encode")
    @delete_original()
    async def stega_encode(self, ctx, url: str, *, data: str):
        """
        Encode an image using Steganography
        """

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

                    if len(data) == 0:
                        await ctx.send("Missing data!")
                        return

                    new_img = im.copy()
                    self.encode_enc(new_img, data)

                    final_buffer = BytesIO()
                    new_img.save(final_buffer, "png")

                final_buffer.seek(0)
                file = discord.File(filename="encoded.png", fp=final_buffer)
                await ctx.send(file=file)

        except (UnidentifiedImageError, requests.exceptions.MissingSchema):
            await ctx.send("Invalid URL!")
            return

    @group_stega.command(name="decode")
    @delete_original()
    async def stega_decode(self, ctx, url: str):
        """
        Decode an image using Steganography
        """

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

                    data = ''
                    img_data = iter(im.getdata())

                    while True:
                        pixels = [value for value in img_data.__next__()[:3] +
                                  img_data.__next__()[:3] +
                                  img_data.__next__()[:3]]
                        # string of binary data
                        bin_str = ''

                        for i in pixels[:8]:
                            if i % 2 == 0:
                                bin_str += '0'
                            else:
                                bin_str += '1'

                        data += chr(int(bin_str, 2))
                        if pixels[-1] % 2 != 0:
                            # return data
                            await ctx.send(f"**Data:**\n{data}")
                            return

        except (UnidentifiedImageError, requests.exceptions.MissingSchema):
            await ctx.send("Invalid URL!")
            return


def setup(bot):
    bot.add_cog(Utility(bot))
