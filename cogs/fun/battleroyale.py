import random
from collections import defaultdict

import asyncio
import discord
from discord.ext import commands

from util.decorators import delete_original


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="battleroyale", aliases=["br"])
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @delete_original()
    async def battle_royale(self, ctx, delay=3, ignore_bots=True, skip=False):
        """
        Battle Royale of Everyone in the Server!

        Delay - Min: 2, Max: 10
        Skip will skip to results

        """

        delay = max(2, min(10, delay))

        prompts = self.get_prompts()

        users = list(ctx.guild.members)
        if ignore_bots:
            users = list(filter(lambda u: not u.bot, users))

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
                embed.description = f"{prompt.format(f'**{killer.name}**', f'**{user.name}**')}\n\n\nRemaining Users (**{len(users)}**):\n\n{remaining}"[:1900]
                await msg.edit(embed=embed)

                await asyncio.sleep(delay)

        places.append(users[0])
        places.reverse()
        places_text = ""
        index = 1
        for u in places:
            places_text += f"{index} - {u.name} - {user_kills[u]} kills\n"
            index += 1

        embed.description = f"**{users[0].name}** is the winner!\n\n**Places:**\n{places_text}"[:1900]
        await msg.edit(embed=embed)

    @staticmethod
    def get_prompts():
        prompts = [
            "{} killed {} with an axe!",
            "{} slaughtered {} with their looks.",
            "{} murdered {}.",
            "{} beat {} to death with a rainbow trout.",
            "{} sucked the life out of {}.",
            "{} ran over {} with a taco truck.",
            "{} drove {} to the point of insanity."
        ]

        return prompts


def setup(bot):
    bot.add_cog(Fun(bot))
