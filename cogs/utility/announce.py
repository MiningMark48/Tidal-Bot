import textwrap
from io import BytesIO

import discord
from PIL import Image, ImageDraw, ImageFont
from discord.ext import commands


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["announcement"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def announce(self, ctx, *, text: str):
        """Announce a message"""
        await ctx.message.delete()
        
        title_text = "Announcement"
        chars_per_line = 55
        # lines = 8
        line_spacing = 10
        max_chars = 1000

        if len(text) > max_chars:
            return await ctx.send(f'Too many characters! Must be less than `{max_chars}`.')

        async with ctx.typing():
            wrapper = textwrap.TextWrapper(width=chars_per_line)
            w_lines = wrapper.wrap(text=text)

            with Image.new("RGB", (1600, 1600), 0xffffff) as im:
                font_text_size = 34
                font_title = ImageFont.truetype(f'./resources/fonts/impact.ttf', size=48)
                font_name = ImageFont.truetype(f'./resources/fonts/arial.ttf', size=30)
                font_text = ImageFont.truetype(f'./resources/fonts/arial.ttf', size=font_text_size)
                draw = ImageDraw.Draw(im)                

                title_start = (15, 15)
                title_text = title_text.upper()
                name_text = f"- {ctx.author.display_name}"
                title_width, title_height = draw.textsize(title_text, font_title)
                name_width, name_height = draw.textsize(name_text, font_name)
                shape = ((0, 0), (im.size[0], title_height+name_height+(title_start[1]*2)))
                draw.rectangle(shape, fill=ctx.message.author.top_role.color.to_rgb())
                draw.text((title_start[0], title_start[1]-5), title_text, fill=0x000000, font=font_title)
                draw.text((title_start[0]+30, title_start[1]+5+title_height), name_text, fill=0x000000, font=font_name)

                (x, y) = (20, shape[1][1]+20)
                text_w = 400
                y_text = y
                for line in w_lines:
                    new_width = draw.textsize(line, font_text)[0]
                    if new_width > text_w:
                        text_w = new_width
                    draw.text((x, y_text), line, fill=0x000000, font=font_text)
                    y_text += (font_text_size + line_spacing)

                if title_width > text_w:
                    text_w = title_width

                shape_bottom = ((0, y_text+40), (im.size[0], y_text+50))
                draw.rectangle(shape_bottom, fill=ctx.message.author.top_role.color.to_rgb())

                im = im.crop((0, 0, text_w + 50, title_height + y_text))

                final_buffer = BytesIO()
                im.save(final_buffer, "png")

            final_buffer.seek(0)
            file = discord.File(filename="announcement.png", fp=final_buffer)
            await ctx.send(file=file)

    @commands.command(name="announceembed", aliases=["announcementembed", "annembed"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def announce_embed(self, ctx, *, text: str):
        """Announce a message"""
        await ctx.message.delete()

        max_chars = 1900
        if len(text) > max_chars:
            return await ctx.send(f'Too many characters! Must be less than `{max_chars}`.')

        embed = discord.Embed(title="Announcement", color=ctx.message.author.top_role.color)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.description = text
        embed.timestamp = ctx.message.created_at

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Utility(bot))
