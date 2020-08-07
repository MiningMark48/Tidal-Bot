import datetime
import string
from functools import partial
from io import BytesIO
from typing import Union

import aiohttp
import discord
from PIL import Image, ImageDraw, ImageFont
from discord.ext import commands


class Memes(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=bot.loop)

    async def get_avatar(self, user: Union[discord.User, discord.Member]) -> bytes:
        avatar_url = str(user.avatar_url_as(format="png"))
        async with self.session.get(avatar_url) as response:
            avatar_bytes = await response.read()
        return avatar_bytes

    @staticmethod
    def processing(avatar_bytes: bytes, member: discord.Member) -> BytesIO:

        dt = datetime.date.today()
        year = dt.year

        with Image.open("./resources/images/memetemps/template_memelicense.png") as im:
            im = im.convert("RGBA")
            font = ImageFont.truetype(f'./resources/fonts/arial.ttf', size=18)
            font_sig = ImageFont.truetype(f'./resources/fonts/kunstler.ttf', size=48)
            draw = ImageDraw.Draw(im)
            # font_color = member.color.to_rgb()
            font_color = (0,79,74)

            draw.text((510, 135), str(member.id), fill=font_color, font=font)
            draw.text((510, 200), f'#{str(member.discriminator)}', fill=font_color, font=font)
            draw.text((510, 250), member.name, fill=font_color, font=font)

            if member.display_name != member.name and all(c in string.printable for c in member.display_name):
                draw.text((510, 270), member.display_name, fill=font_color, font=font)

            draw.text((820, 135), str(member.created_at.strftime("%m/%d/%Y")), fill=font_color, font=font)
            draw.text((820, 170), str(member.created_at.strftime(f"%m/%d/{int(year)+5}")), fill=font_color, font=font)
            draw.text((540, 445), "C", fill=font_color, font=font)
            draw.text((540, 468), ("NONE" if not member.is_on_mobile() else "MOBL"), fill=font_color, font=font)
            draw.text((505, 512), str(dt.strftime("%m/%d/%Y")), fill=font_color, font=font)

            draw.text((90, 495), str(member.name), fill=0x000000, font=font_sig)           

            avatar = Image.open(BytesIO(avatar_bytes)).convert('RGB').resize((371, 371))
            av_loc = (64, 118)
            im.paste(avatar, av_loc)

            alpha_layer = Image.new('RGBA', im.size, (0,0,0,0))
            av1 = avatar.resize((150,150))
            av1.putalpha(64)
            av2 = av1           
            av2.putalpha(128)
            av2 = av2.convert('LA')

            av1_loc = (725, 300)
            alpha_layer.paste(av1, av1_loc)

            offset = 75
            av2_loc = (av1_loc[0]+offset, av1_loc[1]+offset)
            alpha_layer.paste(av2, av2_loc)

            im = Image.alpha_composite(im, alpha_layer)
            im = im.convert("RGB")

            final_buffer = BytesIO()
            im.save(final_buffer, "png")

        final_buffer.seek(0)
        return final_buffer

    @commands.command(aliases=["licensememe"])
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.guild_only()
    async def memelicense(self, ctx):
        """Create a meme license."""

        member = ctx.author

        async with ctx.typing():
            
            avatar_bytes = await self.get_avatar(member)
            fn = partial(self.processing, avatar_bytes, member)
            final_buffer = await self.bot.loop.run_in_executor(None, fn)

            file = discord.File(filename=f"memelicense_{member.display_name}.png", fp=final_buffer)

            await ctx.send(file=file)

def setup(bot: commands.Bot):
    bot.add_cog(Memes(bot))