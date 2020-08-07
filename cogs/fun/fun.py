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
        self.api_key_tenor = BotConfig().get_api_key('tenor')

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

    @commands.command(name="magic8ball", aliases=["8ball", "magicball", "magic8"])
    async def magic_8_ball(self, ctx):
        """The Magic 8 Ball says..."""
        responses = ["It is certain", "It is decidedly so", "Without a doubt", "Yes - definitely", "You may rely on it",
                     "As I see it, yes", "Most likely", "Outlook good", "Yes", "Signs point to yes",
                     "Reply hazy, try again", "Ask again later", "Better not tell you now", "Cannot predict now",
                     "Concentrate and ask again", "Don't count on it", "My reply is no", "My sources say no",
                     "Outlook not so good", "Very doubtful"]
        rand_resp = random.choice(responses)

        await ctx.send(f"The Magic 8 Ball says... `{rand_resp}`")

    @commands.command()
    async def slap(self, ctx, *, user: str):
        """Slap someone with a fish"""
        await ctx.send(f"*slaps {user} with a fish.* :fish:")

    @commands.command(aliases=["gif"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    @delete_original()
    async def tenor(self, ctx, *, search: str):
        """
        Returns a random GIF based on search term
        """

        api_key = self.api_key_tenor

        if not api_key:
            await ctx.send("Error, missing API key. Report to bot owner.")
            return

        base_url = "https://api.tenor.com/v1/search"
        payload = {"q": search, "key": api_key, "limit": 16}

        async with aiohttp.ClientSession() as session:
            async with session.get(base_url, params=payload) as r:
                content = await r.content.read()

                if r.status == 200:
                    gif_list = json.loads(content)
                    if not gif_list:
                        await ctx.send("Nothing found!")

                    results = gif_list['results']
                    random_gif = random.choice(results)['url']

                    await ctx.send(f"{ctx.author.mention}:\n{random_gif}")
                else:
                    await ctx.send("Nothing found!")

    @commands.command()
    @delete_original()
    async def mock(self, ctx, *, text: typing.Optional[str]):
        """spOngEBoB MoCKifY soMe TeXT"""
        if not text:
            messages = await ctx.channel.history(limit=1).flatten()
            text = messages[0].content

        if text:
            await ctx.send(mockify(text))

    @commands.command(name="nocontext", aliases=["ooc"])
    @commands.cooldown(1, 8, commands.BucketType.channel)
    @delete_original()
    async def out_of_context(self, ctx, limit=500):
        """
        Picks a random message from the channel, out-of-context.

        Min: 10, Max: 10000

        """
        limit = max(min(limit, 10000), 10)

        og_msg = await ctx.send(f"Finding an out-of-context message out of *{limit}*...")

        messages = []
        async for msg in ctx.channel.history(limit=limit):
            messages.append(msg)

        def get_rand_msg():
            rmsg = random.choice(messages)
            if rmsg.content:
                return rmsg
            return get_rand_msg()

        rand_msg = get_rand_msg()
        embed = discord.Embed(title="Out-of-Context Message", color=0x9C10F7)
        embed.description = rand_msg.content
        embed.set_author(name=rand_msg.author, icon_url=rand_msg.author.avatar_url)
        embed.timestamp = rand_msg.created_at
        await og_msg.edit(embed=embed, content="")


def setup(bot):
    bot.add_cog(Fun(bot))
