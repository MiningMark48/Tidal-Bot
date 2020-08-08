import json
import random
import typing

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

        self.new_game = []

    @commands.command(name="blackjack", aliases=["21", "bj"])
    @delete_original()
    async def blackjack(self, ctx):
        """Play a (modified) game of blackjack, simplistic-ly."""

        def check(m):
            return m.author.id == ctx.author.id

        cards = list(range(1, 11))
        cards_dealer = random.sample(cards, 2)
        cards_player = random.sample(cards, 2)

        embed = discord.Embed(title="Blackjack", color=0x076324)
        embed.set_footer(text=f"{ctx.author.display_name}'s game")
        embed.add_field(name="Dealer", value=f"{str(cards_dealer[0])}  ?")
        embed.add_field(name="Player",
                        value=f"{'  '.join(str(c) for c in cards_player)} ({sum(cards_player)})")

        msg = await ctx.send(embed=embed)

        async def play():
            cards_player_sum = sum(cards_player)
            if cards_player_sum == 21:  # Blackjack
                embed.description = "Blackjack! You win!"
                embed.set_field_at(0, name="Dealer",
                                   value=f"{'  '.join(str(c) for c in cards_dealer)} ({sum(cards_dealer)})")
                await msg.edit(embed=embed)
            elif sum(cards_player) > 21:  # Bust
                embed.description = "Bust, dealer wins."
                embed.set_field_at(0, name="Dealer",
                                   value=f"{'  '.join(str(c) for c in cards_dealer)} ({sum(cards_dealer)})")
                await msg.edit(embed=embed)
            else:  # Hit/Stay
                embed.description = "Hit or stay?"
                await msg.edit(embed=embed)
                msg_wf = await self.bot.wait_for('message', check=check, timeout=15)

                if msg_wf.content.lower() == "hit":
                    cards_player.append(random.choice(cards))
                    embed.set_field_at(1, name="Player",
                                       value=f"{'  '.join(str(c) for c in cards_player)} ({sum(cards_player)})")
                    await msg.edit(embed=embed)
                    if isinstance(ctx.channel, discord.TextChannel):
                        await msg_wf.delete()
                    await play()
                elif msg_wf.content.lower() == "stay":
                    cards_player_sum = sum(cards_player)

                    async def card_dealer_draw():  # Dealer keeps drawing until 17 or higher
                        cards_dealer_sum = sum(cards_dealer)

                        if cards_dealer_sum < 17:
                            cards_dealer.append(random.choice(cards))
                            embed.set_field_at(0, name="Dealer",
                                               value=f"{'  '.join(str(c) for c in cards_dealer)} ({sum(cards_dealer)})")
                            await msg.edit(embed=embed)

                            await asyncio.sleep(1)
                            await card_dealer_draw()
                        else:
                            if cards_player_sum > cards_dealer_sum or cards_dealer_sum > 21:
                                embed.description = "Player wins!"
                            elif cards_player_sum < cards_dealer_sum or cards_dealer_sum == 21:
                                embed.description = "Dealer wins."
                            else:
                                embed.description = "It's a push, you both win!"

                    await card_dealer_draw()

                    embed.set_field_at(0, name="Dealer",
                                       value=f"{'  '.join(str(c) for c in cards_dealer)} ({sum(cards_dealer)})")
                    await msg.edit(embed=embed)
                    await msg_wf.delete()

        await play()

        # self.new_game.append(msg.id)
        # await msg.add_reaction("🔁")

    # @commands.Cog.listener("on_raw_reaction_add")
    # async def on_raw_reaction_add(self, payload):
    #     guild = self.bot.get_guild(payload.guild_id)
    #     channel = guild.get_channel(payload.channel_id)
    #     rmsg = await channel.fetch_message(payload.message_id)

    #     if rmsg.id in self.new_game:
    #         reaction_emoji = str(payload.emoji)
    #         user = self.bot.get_user(payload.user_id)
    #         if reaction_emoji == '🔁':
    #             if not user == self.bot.user:
    #                 ctx = await self.bot.get_context(rmsg)
    #                 cmd = self.bot.get_command("blackjack")
    #                 self.new_game.remove(rmsg.id)
    #                 await rmsg.clear_reactions()
    #                 await ctx.invoke(cmd)


def setup(bot):
    bot.add_cog(Fun(bot))
