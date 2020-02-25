import asyncio
import random

import discord
from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    # @commands.cooldown(1, 15, commands.BucketType.user)
    async def battleship(self, ctx):
        """Battleship - WIP"""

        timeout = 15
        reaction_emoji = "🚢"

        embed = discord.Embed(title="Battleship", color=0x34c6eb)
        embed.description = f"{ctx.author.mention} wants to play Battleship!\n\n" \
                            f"To join, react with {reaction_emoji}.\n\n" \
                            f"You have {timeout} seconds to join."

        msg_c = await ctx.send(embed=embed)
        await msg_c.add_reaction(reaction_emoji)

        await asyncio.sleep(timeout)

        players = []
        rmsg = await ctx.channel.fetch_message(msg_c.id)
        for reac in rmsg.reactions:
            if reac.emoji == reaction_emoji:
                async for usr in reac.users():
                    if not usr.bot and not usr == ctx.author:
                        players.append(usr)

        await rmsg.clear_reactions()
        if players:
            player2 = players[0]
            embed.description = f"Lobby closed.\n\n" \
                                f"{ctx.author.mention} vs {player2.mention}\n\n" \
                                f"Game is starting..."
            await rmsg.edit(embed=embed)

            board_p1 = self.gen_board()
            board_p2 = self.gen_board()
            await ctx.author.send(self.board_to_text(board_p1))
            await player2.send(self.board_to_text(board_p2))

            await ctx.send(f'{ctx.author.mention} and {player2.mention}, you\'re boards have been DM\'d to you '
                           f'for reference.', delete_after=15)

            await asyncio.sleep(2)

            await ctx.send(f'{ctx.author.mention}: {self.board_to_text(self.gen_board_blank())}\n'
                           f'{player2.mention}: {self.board_to_text(self.gen_board_blank())}')

        else:
            embed.description = "Nobody joined!\n\n" \
                                "Game ended."
            await rmsg.edit(embed=embed)

        # await ctx.send(self.gen_board())

    # noinspection PyTypeChecker
    @staticmethod
    def gen_board():
        base = 10
        board = [[0 for c in range(base)] for r in range(base)]

        for ship in range(base):
            r_row = board[random.randint(0, len(board)-1)]
            r_row[random.randint(0, len(r_row)-1)] = 1

        return board

    # noinspection PyTypeChecker
    @staticmethod
    def gen_board_blank():
        base = 10
        board = [[0 for c in range(base)] for r in range(base)]
        return board

    @staticmethod
    def board_to_text(board):
        msg = "```"
        msg += "     A  B  C  D  E  F  G  H  I  J\n\n"
        i = 1
        for row in board:
            msg += f"{i}   " if i < 10 else f"{i}  "
            for num in row:
                msg += f' {"s" if num == 1 else "|"} '
            msg += "\n"
            i += 1
        msg += "```"
        return msg


def setup(bot):
    bot.add_cog(Fun(bot))
