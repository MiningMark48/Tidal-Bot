import random

import discord
from discord.ext import commands
import asyncio


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="russianroulette", aliases=["rr", "rroulette"])
    async def russian_roulette(self, ctx):
        """Russian Roulette"""

        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

        timeout = 5
        reaction_emoji = "🔫"

        embed = discord.Embed(title="Russian Roulette", color=0xfc2c03)
        embed.description = f"Starting lobby...\n\n" \
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
                    if not usr.bot:
                        players.append(usr)

        await rmsg.clear_reactions()
        embed.description = f"Lobby closed with {len(players)} player{'' if len(players) == 1 else 's'}.\n\n" \
                            f"Game is starting..."
        await rmsg.edit(embed=embed)
        await asyncio.sleep(2)

        if players:
            dead_player = random.choice(players)
            for player in players:
                if player != dead_player:
                    await ctx.send(f'{player.mention} pulls the trigger, it clicks. Safe.', delete_after=10)
                else:
                    await ctx.send(f'{player.mention} pulls the trigger, BAM! Dead.', delete_after=10)
                    break
                await asyncio.sleep(3)
            embed.description = f"Game ended.\n\n{dead_player.mention} lost."
            await rmsg.edit(embed=embed)
        else:
            await ctx.send("Nobody joined the game. :(")


def setup(bot):
    bot.add_cog(Fun(bot))
