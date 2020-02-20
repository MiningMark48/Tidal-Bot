import discord
import datetime
import calendar
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from discord.ext import commands
from io import BytesIO


class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["progressbar"])
    @commands.cooldown(2, 30, commands.BucketType.user)
    async def progress(self, ctx):
        """See how far into the year we are."""
        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

        async with ctx.typing():
            with Image.new("RGB", (800, 400), 0xffffff) as im:
                
                dt = datetime.date.today()
                year = dt.year
                day = int(dt.strftime("%j"))
                is_leap = calendar.isleap(year)
                total_days = 365 if not is_leap else 366

                percentage = round((day/total_days)*100)

                text = f'{year} is {percentage}% complete.'

                font_size = 70
                font = ImageFont.truetype(f'./fonts/arial.ttf', size=font_size)
                draw = ImageDraw.Draw(im)

                w, h = im.size
                spacing = 25
                shape_h = 75
                prog_width = w-spacing
                outline_size = 5
                shape_bg = ((spacing, (h/2)-(shape_h/2)), (prog_width, (h/2)+(shape_h/2)))
                shape_bg2 = ((spacing-outline_size, (h/2)-(shape_h/2)-outline_size), (prog_width+outline_size, (h/2)+(shape_h/2)+outline_size))
                shape_fg = ((spacing, (h/2)-(shape_h/2)), (((prog_width/100)*percentage)+(spacing/2), (h/2)+(shape_h/2)))

                draw.rectangle(shape_bg2, fill=0x000000)
                draw.rectangle(shape_bg, fill=0xffffff)

                try:
                    draw.rectangle(shape_fg, fill=ctx.message.author.top_role.color.to_rgb())
                except AttributeError:
                    draw.rectangle(shape_fg, fill=0x00ff00)

                tw = draw.textsize(text, font)[0]
                draw.text(((w-tw)/2, 25), text, fill=0x000000, font=font)

                im = im.crop((0, 0, w, (h/2)+(shape_h/2)+spacing))

                final_buffer = BytesIO()
                im.save(final_buffer, "png")

            final_buffer.seek(0)
            file = discord.File(filename=f"progressbar_{year}.png", fp=final_buffer)
            await ctx.send(file=file)


def setup(bot):
    bot.add_cog(Images(bot))
