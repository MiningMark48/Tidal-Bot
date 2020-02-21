from random import sample

import discord
from PIL import Image, ImageDraw, ImageFont
from discord.ext import commands
from functools import partial
from io import BytesIO


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def processing(board) -> BytesIO:

        with Image.open("./templates/template_sudoku.png") as im:
            im = im.convert("RGB")
            font = ImageFont.truetype(f'./fonts/arial.ttf', size=28)
            draw = ImageDraw.Draw(im)
            font_color = (0, 0, 0)

            # draw.text((510, 135), str(member.id), fill=font_color, font=font)

            for i in range(len(board)):
                for j in range(len(board[i])):
                    num = board[i][j]
                    base_pos = 20
                    spacing = 57
                    pos = (base_pos + (spacing * i), base_pos + (spacing * j) - 3)
                    if num != 0:
                        draw.text(pos, str(num), fill=font_color, font=font)

            final_buffer = BytesIO()
            im.save(final_buffer, "png")

        final_buffer.seek(0)
        return final_buffer

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def sudoku(self, ctx, dm_solution=True):
        """Generate a Sudoku puzzle auto-magically"""
        async with ctx.typing():
            base = 3
            board = self.gen_board(base)
            
            if dm_solution:
                # Solved board, DM to user
                fn_s = partial(self.processing, board)
                final_buffer_s = await self.bot.loop.run_in_executor(None, fn_s)
                file_s = discord.File(filename="SPOILER_sudoku_solved.png", fp=final_buffer_s)
    
                await ctx.author.send(file=file_s,
                                      content="Sudoku solution: ")

            # With blanks
            fn = partial(self.processing, self.create_blanks(base, board))
            final_buffer = await self.bot.loop.run_in_executor(None, fn)
            file = discord.File(filename="sudoku.png", fp=final_buffer)

            dm_message = "The solution was DM\'d to you." 
            await ctx.send(file=file,
                           content=f'{ctx.author.mention}, here\'s your puzzle! {dm_message if dm_solution else ""}')

    # noinspection PyTypeChecker
    @staticmethod
    def gen_board(base):
        side = base * base

        # Base valid solution patters
        def pattern(r, c):
            return (base * (r % base) + r // base + c) % side

        # Randomize rows, columns and numbers from the valid base pattern
        def shuffle(s):
            return sample(s, len(s))

        r_base = range(base)
        rows = [g * base + r for g in shuffle(r_base) for r in shuffle(r_base)]
        cols = [g * base + c for g in shuffle(r_base) for c in shuffle(r_base)]
        nums = shuffle(range(1, base * base + 1))

        # Make the board using randomized baseline pattern
        board = [[nums[pattern(r, c)] for c in cols] for r in rows]

        return board

    @staticmethod
    def create_blanks(base, board):
        side = base * base
        board_squares = side * side
        empty_spaces = board_squares * 3 // 4
        for p in sample(range(board_squares), empty_spaces):
            board[p // side][p % side] = 0
        return board


def setup(bot):
    bot.add_cog(Fun(bot))
