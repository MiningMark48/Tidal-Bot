import discord
import aiohttp
import os
import textwrap
import random
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from functools import partial
from io import BytesIO
from util.spongemock import mockify

class Memes(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=bot.loop)

    def draw_text(self, draw, line, pos, font, font_color, outlined=False):
        (x,y) = pos
        if outlined:
            pos_o = [(x-1,y-1),(x+1,y-1),(x-1,y+1),(x+1,y+1)]
            for p in pos_o:
                draw.text(p, line, font=font, fill=0x000000)
        draw.text((x, y), line, fill=font_color, font=font)

    def processing_drawtext(self, text: list, template_name: str, base_pos=(0,0), font_size=55, font_color=0x000000, font_name="arial", centered=False, outlined=False) -> BytesIO:
        return self.processing_drawtext_multi([text], template_name, [base_pos], font_size, font_color, font_name, centered, outlined)

    def processing_drawtext_multi(self, text: list, template_name: str, base_pos=list, font_size=55, font_color=0x000000, font_name="arial", centered=False, outlined=False) -> BytesIO:

        with Image.open("./templates/template_{}".format(template_name)) as im:
            font = ImageFont.truetype(f'./fonts/{font_name}.ttf', size=font_size)
            text_draw = ImageDraw.Draw(im)

            for entry in base_pos:
                (x, y) = entry
                y_text = y
                for line in text[base_pos.index(entry)]:
                    if centered:
                        w, h = im.size
                        tw, th = text_draw.textsize(str(line), font)
                        self.draw_text(text_draw, line, (((w-tw)/2), y_text), font, font_color, outlined)
                    else:
                        self.draw_text(text_draw, line, (x, y_text), font, font_color, outlined)
                    y_text += (font_size + 5)

            final_buffer = BytesIO()
            im.save(final_buffer, "png")

        final_buffer.seek(0)
        return final_buffer

    @staticmethod
    def processing_drawtext_snapchat(text: str, template_name: str, height=0, scale=1, font_color=0xffffffff) -> BytesIO:
        font_size = 24 * scale

        with Image.open("./templates/template_{}".format(template_name)) as im:
            im = im.convert("RGBA")
            im_o = Image.new('RGBA', im.size, (0,0,0,0))
            font = ImageFont.truetype('./fonts/arial.ttf', size=font_size)
            draw = ImageDraw.Draw(im_o)

            w, h = im.size
            tw, th = draw.textsize(text, font)
            shape_h = 35 * scale
            shape = ((0, height), (w, height+shape_h))
            draw.rectangle(shape, fill=(0,0,0,160))
            
            draw.text(((w-tw)/2, height+(shape_h-th)/2), text, fill=font_color, font=font)

            im = Image.alpha_composite(im, im_o)
            im = im.convert("RGB")

            final_buffer = BytesIO()
            im.save(final_buffer, "png")

        final_buffer.seek(0)
        return final_buffer

    async def try_delete(self, ctx):
        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def dashdefine(self, ctx, *, text: str):
        """It defined who I am"""
        await self.try_delete(ctx)
        chars_per_line = 28
        lines = 3

        max_chars = chars_per_line * lines
        if len(text) > max_chars:
            return await ctx.send(f'Too many characters! Must be less than `{max_chars}`.')

        async with ctx.typing():
            wrapper = textwrap.TextWrapper(width=chars_per_line)
            lines = wrapper.wrap(text=text)
            fn = partial(self.processing_drawtext, lines, "dashdefine.png", (20, 20), 55)
            final_buffer = await self.bot.loop.run_in_executor(None, fn)
            file = discord.File(filename="dashdefine.png", fp=final_buffer)
            await ctx.send(file=file)

    @commands.command(name="draw25")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def draw_twofive(self, ctx, *, text: str):
        """...or draw 25 cards"""
        await self.try_delete(ctx)
        chars_per_line = 15
        lines = 5

        max_chars = chars_per_line * lines
        if len(text) > max_chars:
            return await ctx.send(f'Too many characters! Must be less than `{max_chars}`.')

        async with ctx.typing():
            wrapper = textwrap.TextWrapper(width=chars_per_line)
            lines = wrapper.wrap(text=text.upper())
            fn = partial(self.processing_drawtext, lines, "draw25.png", (125, 125), 24, font_color=0xffffff, font_name="impact", outlined=True)
            final_buffer = await self.bot.loop.run_in_executor(None, fn)
            file = discord.File(filename="draw25.png", fp=final_buffer)
            await ctx.send(file=file)

    @commands.command(name="exit12")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def exit(self, ctx, text1: str, text2: str, text3: str):
        """
        Left, Exit 12. *Screech*

        Note: This will likely require quotes.
        """
        await self.try_delete(ctx)
        chars_per_line = 10
        lines = 5

        max_chars = chars_per_line * lines
        if len(text1) > max_chars or len(text2) > max_chars or len(text3) > max_chars:
            return await ctx.send(f'Too many characters! Must be less than `{max_chars}`.')

        async with ctx.typing():
            wrapper = textwrap.TextWrapper(width=chars_per_line)
            lines1 = wrapper.wrap(text=text1)
            lines2 = wrapper.wrap(text=text2)
            lines3 = wrapper.wrap(text=text3)
            fn = partial(self.processing_drawtext_multi, [lines1, lines2, lines3], "exit12.png", [(200, 100), (420, 100), (415, 540)], 30, 0xffffff)
            final_buffer = await self.bot.loop.run_in_executor(None, fn)
            file = discord.File(filename="exit12.png", fp=final_buffer)
            await ctx.send(file=file)

    @commands.command(name="financialsupport")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def financial_support(self, ctx, *, text: str):
        """Financially support me plz"""
        await self.try_delete(ctx)
        chars_per_line = 30
        lines = 3

        max_chars = chars_per_line * lines
        if len(text) > max_chars:
            return await ctx.send(f'Too many characters! Must be less than `{max_chars}`.')

        async with ctx.typing():
            wrapper = textwrap.TextWrapper(width=chars_per_line)
            lines = wrapper.wrap(text=text)
            fn = partial(self.processing_drawtext, lines, "financialsupport.png", (20, 20), 40, centered=True)
            final_buffer = await self.bot.loop.run_in_executor(None, fn)
            file = discord.File(filename="finan_support.png", fp=final_buffer)
            await ctx.send(file=file)

    @commands.command(name="flextape", aliases=["philswift", "flexon", "flexseal"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def flex_tape(self, ctx, text1: str, text2: str, text3: str):
        """
        Flex on!

        Note: This will likely require quotes.
        """
        await self.try_delete(ctx)
        chars_per_line = 10
        lines = 3

        max_chars = chars_per_line * lines
        if len(text1) > max_chars or len(text2) > max_chars or len(text3) > max_chars:
            return await ctx.send(f'Too many characters! Must be less than `{max_chars}`.')

        async with ctx.typing():
            wrapper = textwrap.TextWrapper(width=chars_per_line)
            lines1 = wrapper.wrap(text=text1.upper())
            lines2 = wrapper.wrap(text=text2.upper())
            lines3 = wrapper.wrap(text=text3.upper())
            fn = partial(self.processing_drawtext_multi, [lines1, lines2, lines3], "flextape.png",
                         [(80, 115), (350, 115), (230, 370)], 30, 0xffffff, font_name="impact", outlined=True)
            final_buffer = await self.bot.loop.run_in_executor(None, fn)
            file = discord.File(filename="flex_tape.png", fp=final_buffer)
            await ctx.send(file=file)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def kkchum(self, ctx, text1: str, text2: str):
        """
        Krusty Krab > Chum Bucket
        """
        await self.try_delete(ctx)
        chars_per_line = 15
        lines = 2

        max_chars = chars_per_line * lines
        if len(text1) > max_chars or len(text2) > max_chars:
            return await ctx.send(f'Too many characters! Must be less than `{max_chars}`.')

        async with ctx.typing():
            wrapper = textwrap.TextWrapper(width=chars_per_line)
            lines1 = wrapper.wrap(text=text1.upper())
            lines2 = wrapper.wrap(text=text2.upper())
            fn = partial(self.processing_drawtext_multi, [lines1, lines2], "kkchum.jpg", [(165, 40), (200, 460)], 40, 0xffffff, "impact", centered=False, outlined=True)
            final_buffer = await self.bot.loop.run_in_executor(None, fn)
            file = discord.File(filename="kkchum.png", fp=final_buffer)
            await ctx.send(file=file)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def linus(self, ctx, *, text: str):
        """
        Linus selfies ftw.
        """
        await self.try_delete(ctx)
        max_chars = 60
        if len(text) > max_chars:
            return await ctx.send(f'Too many characters! Must be less than `{max_chars}`.')

        async with ctx.typing():
            fn = partial(self.processing_drawtext_snapchat, text, "linus.jpg", random.randint(250, 450))
            final_buffer = await self.bot.loop.run_in_executor(None, fn)
            file = discord.File(filename="linus.png", fp=final_buffer)
            await ctx.send(file=file)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def nobrain(self, ctx, *, text: str):
        """Oh F***, I forgot to give you a brain."""
        await self.try_delete(ctx)
        chars_per_line = 20
        lines = 3

        max_chars = chars_per_line * lines
        if len(text) > max_chars:
            return await ctx.send(f'Too many characters! Must be less than `{max_chars}`.')

        async with ctx.typing():
            wrapper = textwrap.TextWrapper(width=chars_per_line)
            lines = wrapper.wrap(text=text)
            fn = partial(self.processing_drawtext, lines, "nobrain.jpg", (40, 380), 24)
            final_buffer = await self.bot.loop.run_in_executor(None, fn)
            file = discord.File(filename="nobrain.png", fp=final_buffer)
            await ctx.send(file=file)

    @commands.command(name="nothere")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def not_here(self, ctx, *, text: str):
        """We don't do that here."""
        await self.try_delete(ctx)
        chars_per_line = 35
        lines = 3

        max_chars = chars_per_line * lines
        if len(text) > max_chars:
            return await ctx.send(f'Too many characters! Must be less than `{max_chars}`.')

        async with ctx.typing():
            wrapper = textwrap.TextWrapper(width=chars_per_line)
            lines = wrapper.wrap(text=text)
            fn = partial(self.processing_drawtext, lines, "nothere.png", (20, 20), 28, centered=True)
            final_buffer = await self.bot.loop.run_in_executor(None, fn)
            file = discord.File(filename="not_here.png", fp=final_buffer)
            await ctx.send(file=file)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def patrickpush(self, ctx, text1: str, text2: str):
        """
        PUSH IT SOMEWHERE ELSE!
        """
        await self.try_delete(ctx)
        chars_per_line = 23
        lines = 2

        max_chars = chars_per_line * lines
        if len(text1) > max_chars or len(text2) > max_chars:
            return await ctx.send(f'Too many characters! Must be less than `{max_chars}`.')

        async with ctx.typing():
            wrapper = textwrap.TextWrapper(width=chars_per_line)
            lines1 = wrapper.wrap(text=text1.upper())
            lines2 = wrapper.wrap(text=text2.upper())
            fn = partial(self.processing_drawtext_multi, [lines1, lines2], "patrickpush.jpg", [(0, 5), (0, 525)], 30,
                         0xffffff, "impact", centered=True, outlined=True)
            final_buffer = await self.bot.loop.run_in_executor(None, fn)
            file = discord.File(filename="patrickpush.png", fp=final_buffer)
            await ctx.send(file=file)

    @commands.command(name="pelosirip", aliases=['pelrip'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pelosi_rip(self, ctx, *, text: str):
        """*Rips speech*"""
        await self.try_delete(ctx)
        chars_per_line = 15
        lines = 2

        max_chars = chars_per_line * lines
        if len(text) > max_chars:
            return await ctx.send(f'Too many characters! Must be less than `{max_chars}`.')

        async with ctx.typing():
            wrapper = textwrap.TextWrapper(width=chars_per_line)
            lines = wrapper.wrap(text=text.upper())
            fn = partial(self.processing_drawtext, lines, "pelosirip.png", (515, 255), 30, font_color=0xffffff,
                         font_name="impact", outlined=True)
            final_buffer = await self.bot.loop.run_in_executor(None, fn)
            file = discord.File(filename="pelosi_rip.png", fp=final_buffer)
            await ctx.send(file=file)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def shocked(self, ctx, *, text: str):
        """O_O"""
        await self.try_delete(ctx)
        chars_per_line = 38
        lines = 2

        max_chars = chars_per_line * lines
        if len(text) > max_chars:
            return await ctx.send(f'Too many characters! Must be less than `{max_chars}`.')

        async with ctx.typing():
            wrapper = textwrap.TextWrapper(width=chars_per_line)
            lines = wrapper.wrap(text=text)
            fn = partial(self.processing_drawtext, lines, "shocked.png", (20, 20), 32)
            final_buffer = await self.bot.loop.run_in_executor(None, fn)
            file = discord.File(filename="shocked.png", fp=final_buffer)
            await ctx.send(file=file)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def spongebreathe(self, ctx, *, text: str):
        """*Breathe in* Shit."""
        await self.try_delete(ctx)
        chars_per_line = 20
        lines = 3

        max_chars = chars_per_line * lines
        if len(text) > max_chars:
            return await ctx.send(f'Too many characters! Must be less than `{max_chars}`.')

        async with ctx.typing():
            wrapper = textwrap.TextWrapper(width=chars_per_line)
            lines = wrapper.wrap(text=text)
            fn = partial(self.processing_drawtext, lines, "spongebreathe.jpg", (30, 30))
            final_buffer = await self.bot.loop.run_in_executor(None, fn)
            file = discord.File(filename="spongebreathe.png", fp=final_buffer)
            await ctx.send(file=file)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def spongemock(self, ctx, *, text: str):
        """spOngEBoB MoCKifY soMe TeXT"""
        await self.try_delete(ctx)
        chars_per_line = 35
        lines = 3

        max_chars = chars_per_line * lines
        if len(text) > max_chars:
            return await ctx.send(f'Too many characters! Must be less than `{max_chars}`.')

        async with ctx.typing():
            wrapper = textwrap.TextWrapper(width=chars_per_line)
            lines = wrapper.wrap(text=mockify(text))
            fn = partial(self.processing_drawtext, lines, "spongemock.png", (20, 20), 40, centered=True)
            final_buffer = await self.bot.loop.run_in_executor(None, fn)
            file = discord.File(filename="spongemock.png", fp=final_buffer)
            await ctx.send(file=file)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def spongeout(self, ctx, *, text: str):
        """'Ight, Imma head out"""
        await self.try_delete(ctx)
        chars_per_line = 25
        lines = 3

        max_chars = chars_per_line * lines
        if len(text) > max_chars:
            return await ctx.send(f'Too many characters! Must be less than `{max_chars}`.')

        async with ctx.typing():
            wrapper = textwrap.TextWrapper(width=chars_per_line)
            lines = wrapper.wrap(text=text)
            fn = partial(self.processing_drawtext, lines, "spongeout.png", (20, 20), 40, centered=True)
            final_buffer = await self.bot.loop.run_in_executor(None, fn)
            file = discord.File(filename="spongeout.png", fp=final_buffer)
            await ctx.send(file=file)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def tea(self, ctx, text1: str, text2="But that's none of my business"):
        """
        *Sips tea*
        """
        await self.try_delete(ctx)
        chars_per_line = 24
        lines = 2

        max_chars = chars_per_line * lines
        if len(text1) > max_chars or len(text2) > max_chars:
            return await ctx.send(f'Too many characters! Must be less than `{max_chars}`.')

        async with ctx.typing():
            wrapper = textwrap.TextWrapper(width=chars_per_line)
            lines1 = wrapper.wrap(text=text1.upper())
            lines2 = wrapper.wrap(text=text2.upper())
            fn = partial(self.processing_drawtext_multi, [lines1, lines2], "tea.jpg", [(0, 5), (0, 475)], 55, 0xffffff, "impact", centered=True, outlined=True)
            final_buffer = await self.bot.loop.run_in_executor(None, fn)
            file = discord.File(filename="tea.png", fp=final_buffer)
            await ctx.send(file=file)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def twobuttons(self, ctx, text1: str, text2: str):
        """
        Two buttons! *queue sweating*

        Note: This will likely require quotes.        
        """
        await self.try_delete(ctx)
        chars_per_line = 10
        lines = 2

        max_chars = chars_per_line * lines
        if len(text1) > max_chars or len(text2) > max_chars:
            return await ctx.send(f'Too many characters! Must be less than `{max_chars}`.')

        async with ctx.typing():
            wrapper = textwrap.TextWrapper(width=chars_per_line)
            lines1 = wrapper.wrap(text=text1)
            lines2 = wrapper.wrap(text=text2)
            fn = partial(self.processing_drawtext_multi, [lines1, lines2], "twobuttons.png", [(80, 80), (240, 50)], 30)
            final_buffer = await self.bot.loop.run_in_executor(None, fn)
            file = discord.File(filename="twobuttons.png", fp=final_buffer)
            await ctx.send(file=file)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def win(self, ctx, text1: str, text2: str):
        """
        Who would win?   
        """
        await self.try_delete(ctx)
        chars_per_line = 15
        lines = 10

        max_chars = chars_per_line * lines
        if len(text1) > max_chars or len(text2) > max_chars:
            return await ctx.send(f'Too many characters! Must be less than `{max_chars}`.')

        async with ctx.typing():
            wrapper = textwrap.TextWrapper(width=chars_per_line)
            lines1 = wrapper.wrap(text=text1)
            lines2 = wrapper.wrap(text=text2)
            fn = partial(self.processing_drawtext_multi, [lines1, lines2], "win.png", [(20, 100), (370, 100)], 30)
            final_buffer = await self.bot.loop.run_in_executor(None, fn)
            file = discord.File(filename="win.png", fp=final_buffer)
            await ctx.send(file=file)


def setup(bot: commands.Bot):
    bot.add_cog(Memes(bot))