import calendar
import datetime
from io import BytesIO

import discord
from PIL import Image, ImageDraw, ImageFont
from discord.ext import commands

from util.decorators import delete_original


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["progressbar"])
    @commands.cooldown(2, 30, commands.BucketType.user)
    @delete_original()
    async def progress(self, ctx):
        """See how far into the year we are."""

        async with ctx.typing():
            with Image.new("RGB", (800, 400), 0x202225) as im:
                
                dt = datetime.date.today()
                year = dt.year
                day = int(dt.strftime("%j"))
                is_leap = calendar.isleap(year)
                total_days = 365 if not is_leap else 366

                percentage = round((day/total_days)*100)

                text = f'{year} is {percentage}% complete'

                font_size = 70
                font = ImageFont.truetype(f'./resources/fonts/arial.ttf', size=font_size)
                draw = ImageDraw.Draw(im)

                w, h = im.size
                spacing = 25
                shape_h = 75
                prog_width = w-spacing
                outline_size = 5
                shape_bg = ((spacing, (h/2)-(shape_h/2)), (prog_width, (h/2)+(shape_h/2)))
                shape_bg2 = ((spacing-outline_size, (h/2)-(shape_h/2)-outline_size), (prog_width+outline_size, (h/2)+(shape_h/2)+outline_size))
                shape_fg = ((spacing, (h/2)-(shape_h/2)), (((prog_width/100)*percentage)+(spacing/2), (h/2)+(shape_h/2)))

                draw.rectangle(shape_bg2, fill=0xffffff)
                draw.rectangle(shape_bg, fill=0x2f3136)

                if isinstance(ctx.channel, discord.TextChannel):
                    draw.rectangle(shape_fg, fill=ctx.message.author.top_role.color.to_rgb())
                else:
                    draw.rectangle(shape_fg, fill=0xb9ae92)

                tw = draw.textsize(text, font)[0]
                draw.text(((w-tw)/2, 35), text, fill=0xffffff, font=font)

                im = im.crop((0, 0, w, (h/2)+(shape_h/2)+spacing))

                final_buffer = BytesIO()
                im.save(final_buffer, "png")

            final_buffer.seek(0)
            file = discord.File(filename=f"progressbar_{year}.png", fp=final_buffer)

            embed = discord.Embed(title="Year Progress", color=0xb9ae92)
            if isinstance(ctx.channel, discord.TextChannel):
                embed.__setattr__("color", ctx.message.author.top_role.color)
            embed.set_image(url=f"attachment://progressbar_{year}.png")
            embed.timestamp = ctx.message.created_at

            await ctx.send(file=file, embed=embed)


def setup(bot):
    bot.add_cog(Utility(bot))
