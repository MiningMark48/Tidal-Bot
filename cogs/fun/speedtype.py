import asyncio
import textwrap
import time
from difflib import SequenceMatcher
from io import BytesIO

import discord
from PIL import ImageFont, ImageDraw, Image
from discord.ext import commands
from faker import Faker


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.fake = Faker("en_US")

    @staticmethod
    def process_image(text):
        chars_per_line = 55
        line_spacing = 10

        wrapper = textwrap.TextWrapper(width=chars_per_line)
        w_lines = wrapper.wrap(text=text)

        with Image.new("RGB", (950, 400), 0xffffff) as im:
            font_text_size = 30
            font_text = ImageFont.truetype(f'./resources/fonts/arial.ttf', size=font_text_size)
            draw = ImageDraw.Draw(im)

            (x, y) = (10, 10)
            text_w = 20
            y_text = y
            for line in w_lines:
                new_width = draw.textsize(line, font_text)[0]
                if new_width > text_w:
                    text_w = new_width + 50
                draw.text((x, y_text), line, fill=0x000000, font=font_text)
                y_text += (font_text_size + line_spacing)

            im = im.crop((0, 0, text_w, y_text))

            final_buffer = BytesIO()
            im.save(final_buffer, "png")

        final_buffer.seek(0)
        file = discord.File(filename="speedtype.png", fp=final_buffer)
        return file

    @commands.command(name="speedtype")
    @commands.cooldown(2, 8, commands.BucketType.channel)
    async def speed_type(self, ctx, max_words=5, accuracy_ratio=1.0):
        """
        See who can type the fastest!

        Words Min 1, Max 50

        Accuracy Ratio is 0-1.0 with 0.25 being 25%, etc.
        """

        max_words = max(min(max_words, 50), 1)
        timeout_time = max_words * 2

        def check(m):
            return m.channel == ctx.channel

        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.message.delete()

        rand_text_words = self.fake.words(nb=max_words, ext_word_list=None)
        rand_text = ' '.join(x for x in rand_text_words)
        rand_text = rand_text.replace("\n", " ")

        message = f"**Speed Type!**\nType the following phrase. You have **{timeout_time}** seconds."

        msg = await ctx.send(content=message, file=self.process_image(rand_text))

        start_time = time.time()
        while True:
            if time.time() >= start_time + timeout_time:
                await msg.edit(content="Time ran out!")
                break

            try:
                guess_msg = await self.bot.wait_for('message', check=check, timeout=timeout_time)
            except asyncio.TimeoutError:
                await msg.edit(content="Time ran out!")
                break

            guess = str(guess_msg.clean_content.lower())

            # Accuracy Calculation
            acc = SequenceMatcher(None, guess, str(rand_text).lower()).ratio()

            if acc >= accuracy_ratio:
                await guess_msg.delete()

                time_taken = round(time.time() - start_time, 2)
                wpm = round((max_words/time_taken)*60)
                final_msg = f"**{guess_msg.author.mention}** typed the fastest!\n\n" \
                            f"**Time Took:** {time_taken} seconds\n" \
                            f"**WPM:** {wpm}\n"
                if accuracy_ratio != 1.0:
                    final_msg += f"**Accuracy:** {round(acc / 1 * 100, 1)}% " \
                                 f"(Min: {round(accuracy_ratio / 1 * 100, 1)}%)"
                await msg.edit(content=final_msg)
                break


def setup(bot):
    bot.add_cog(Fun(bot))
