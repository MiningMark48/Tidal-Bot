import random
import typing

import discord
import requests
from discord.ext import commands

from util.spongemock import mockify


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="bubblewrap")
    async def bubble_wrap(self, ctx):
        """Satisfying popping"""
        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

        rows = 10
        columns = 10
        grid = [["||     ||" for n in range(columns)] for n in range(rows)]
        sb = []
        for rws in grid:
            sb.append(''.join(map(str, rws)))
        sb = '\n'.join(sb)

        final = f'{ctx.author.mention}, here\'s your bubble wrap!\n\n' \
                f'{sb}\n\n'

        await ctx.send(final)

    @commands.command(name="chucknorris", aliases=["chuck", "norris"])
    async def chuck_norris(self, ctx):
        """Fetch a Chuck Norris Joke"""
        base_url = "http://api.icndb.com/jokes/random"
        payload = {"escape": "html"}
        r = requests.get(base_url, params=payload, timeout=1)
        content = r.json()
        joke = content["value"]
        joke_text = joke["joke"]
        categories = joke["categories"]

        embed = discord.Embed(title="Chuck Norris")
        embed.description = joke_text
        embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Chuck_Norris_May_2015.jpg/"
                            "220px-Chuck_Norris_May_2015.jpg")
        embed.set_footer(text="Fetched from The Internet Chuck Norris Database")

        if categories:
            embed.add_field(name="Categories", value=" ,".join(str(c).capitalize() for c in categories), inline=False)

        await ctx.send(embed=embed)

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

    @commands.command()
    async def mock(self, ctx, *, text: typing.Optional[str]):
        """spOngEBoB MoCKifY soMe TeXT"""
        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass
        if not text:
            messages = await ctx.channel.history(limit=1).flatten()
            text = messages[0].content

        if text:
            await ctx.send(mockify(text))


def setup(bot):
    bot.add_cog(Fun(bot))

