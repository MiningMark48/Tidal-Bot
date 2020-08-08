import asyncio
import random

import discord
from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.new_game = []

    @commands.command(name="russianroulette", aliases=["rr", "rroulette"])
    async def russian_roulette(self, ctx, chance=6):
        """
        Russian Roulette

        Chance to die: Min of 2, max of 10, default of 6
        """

        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

        chance = max(2, min(chance, 10))

        timeout = 10
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
            player_dead = None
            i = 0
            while not player_dead:
                if i == len(players) * 3:
                    player_dead = random.choice(players)
                    embed.description = f"{player_dead.mention} pulls the trigger, BAM! Dead."
                    await rmsg.edit(embed=embed)
                    break

                for player in players:
                    rand_num = random.randint(1, chance)
                    if rand_num != 1:
                        embed.description = f"{player.mention} pulls the trigger, it clicks. Safe."
                        await rmsg.edit(embed=embed)
                    else:
                        embed.description = f"{player.mention} pulls the trigger, BAM! Dead."
                        await rmsg.edit(embed=embed)
                        player_dead = player
                        break
                    i += 1
                    await asyncio.sleep(2)

            # embed.description = f"Game ended.\n\n{player_dead.mention} died."
            # await rmsg.edit(embed=embed)

            self.new_game.append(rmsg.id)
            await rmsg.add_reaction("🔁")
        else:
            embed.description = "Nobody joined the game :("
            await rmsg.edit(embed=embed)

    @commands.Cog.listener("on_raw_reaction_add")
    async def on_raw_reaction_add(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        rmsg = await channel.fetch_message(payload.message_id)

        if rmsg.id in self.new_game:
            reaction_emoji = str(payload.emoji)
            user = self.bot.get_user(payload.user_id)
            if reaction_emoji == '🔁':
                if not user == self.bot.user:
                    ctx = await self.bot.get_context(rmsg)
                    cmd = self.bot.get_command("russianroulette")
                    self.new_game.remove(rmsg.id)
                    await rmsg.clear_reactions()
                    await ctx.invoke(cmd)

def setup(bot):
    bot.add_cog(Fun(bot))
