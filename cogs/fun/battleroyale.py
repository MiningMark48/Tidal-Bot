import json
import random
import typing
from collections import defaultdict

import aiohttp
import asyncio
import discord
from discord.ext import commands

from util.config import BotConfig
from util.decorators import delete_original
from util.spongemock import mockify


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="battleroyale", aliases=["br"])
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @delete_original()
    async def battle_royale(self, ctx, delay=3, skip=False):
        """
        Battle Royale of Everyone in the Server!

        Delay - Min: 2, Max: 10
        Skip will skip to results

        """

        delay = max(2, min(10, delay))

        prompts = ["{} killed {} with an axe!", "{} slaughtered {} with their looks.", "{} murdered {}.", "{} beat {} to death with a rainbow trout."]

        users = list(ctx.guild.members)

        user_kills = defaultdict(int)
        places = []

        embed = discord.Embed(title="Battle Royale", color=0xf0f0f0)
        embed.description = "Starting..."
        msg = await ctx.send(embed=embed)

        await asyncio.sleep(delay)

        while len(users) > 1:
            user = users.pop(random.randint(0, len(users) - 1))
            killer = random.choice(users)
            prompt = random.choice(prompts)

            user_kills[killer] += 1
            places.append(user)

            remaining = ', '.join(x.name for x in users)
            if not skip:
                embed.description = f"{prompt.format(f'**{killer.name}**', f'**{user.name}**')}\n\n\nRemaining Users (**{len(users)}**):\n\n{remaining}"
                await msg.edit(embed=embed)

                await asyncio.sleep(delay)

        places.append(users[0])
        places.reverse()
        places_text = ""
        index = 1
        for u in places:
            places_text += f"{index} - {u.name} - {user_kills[u]} kills\n"
            index += 1

        embed.description = f"**{users[0].name}** is the winner!\n\n**Places:**\n{places_text}"
        await msg.edit(embed=embed)


def setup(bot):
    bot.add_cog(Fun(bot))
