import random
import asyncio
import discord
from discord.ext import commands

from util.decorators import delete_original


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="tictactoe", aliases=["ttt"])
    @delete_original()
    async def tic_tac_toe(self, ctx, opponent: discord.Member):
        """[WIP] Play Tic-Tac-Toe with a selected player!"""

        emoji_join = "\N{RAISED HAND WITH FINGERS SPLAYED}"
        current_game_board = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

        def check_join(e, u):
            return u.id == opponent.id

        embed = discord.Embed(title="Tic-Tac-Toe", color=0xff00ff)
        embed.description = f"{opponent.mention}, you have been invited to play Tic-Tac-Toe. \n\nClick the {emoji_join} reaction below to accept."
        msg = await ctx.send(embed=embed)

        await msg.add_reaction(emoji_join)

        try:
            wf_react, _ = await self.bot.wait_for('reaction_add', check=check_join, timeout=15)
            wf_react = str(wf_react.emoji)
        except asyncio.TimeoutError:
            embed.description = "User did not accept the invite. \N{FROWNING FACE WITH OPEN MOUTH}"
            await msg.edit(embed=embed)
            await msg.clear_reactions()
            return

        if wf_react != emoji_join:
            return

        await msg.clear_reactions()
        embed.description = "Starting game..."
        await msg.edit(embed=embed)

        await asyncio.sleep(1)

        embed.description = f"```{self.ascii_board(current_game_board)}```"
        await msg.edit(embed=embed)

    def ascii_board(self, board):
        blank_board = "" \
            "  {} | {} | {}  \n" \
            "----+---+----\n" \
            "  {} | {} | {}  \n" \
            "----+---+----\n" \
            "  {} | {} | {}  \n" \

        board = board[:9]

        blank_board = blank_board.format(
            board[0], board[1], board[2], board[3], board[4], board[5], board[6], board[7], board[8]
        )

        return blank_board


def setup(bot):
    bot.add_cog(Fun(bot))
