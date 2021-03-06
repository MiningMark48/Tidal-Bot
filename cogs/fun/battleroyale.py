import random
from collections import defaultdict

import asyncio
import discord
from discord.ext import commands

from util.decorators import delete_original
from util.messages import MessagesUtil


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.messages_util = MessagesUtil(bot)
        self.new_game = []

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

        self.new_game.append(msg.id)
        await msg.add_reaction("\N{CLOCKWISE RIGHTWARDS AND LEFTWARDS OPEN CIRCLE ARROWS}")

    @commands.Cog.listener("on_raw_reaction_add")
    async def on_raw_reaction_add(self, payload):
        user = self.bot.get_user(payload.user_id)

        if user == self.bot.user:
            return

        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        # rmsg = await channel.fetch_message(payload.message_id)
        rmsg = await self.messages_util.get_message(channel, payload.message_id)

        if rmsg.id in self.new_game:
            reaction_emoji = str(payload.emoji)
            
            if reaction_emoji == '\N{CLOCKWISE RIGHTWARDS AND LEFTWARDS OPEN CIRCLE ARROWS}':
                ctx = await self.bot.get_context(rmsg)
                cmd = self.bot.get_command("battleroyale")
                self.new_game.remove(rmsg.id)
                await rmsg.clear_reactions()
                await ctx.invoke(cmd)

    @staticmethod
    def get_prompts():
        prompts = [
            "{1} was killed by {0}.",
            "{0} killed {1} with an axe!",
            "{0} slaughtered {1} with their looks.",
            "{0} murdered {1}.",
            "{0} beat {1} to death with a rainbow trout.",
            "{0} sucked the life out of {1}.",
            "{0} ran over {1} with a taco truck.",
            "{0} drove {1} to the point of insanity.",
            "{0} ran {1} over with a truck."
        ]

        return prompts

def setup(bot):
    bot.add_cog(Fun(bot))
