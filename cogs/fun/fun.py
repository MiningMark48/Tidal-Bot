import random
import typing

import aiohttp
import discord
from discord.ext import commands

from util.spongemock import mockify


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="chucknorris", aliases=["chuck", "norris"])
    async def chuck_norris(self, ctx):
        """Fetch a Chuck Norris Joke"""
        base_url = "http://api.icndb.com/jokes/random"
        payload = {"escape": "html"}
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url, params=payload) as r:
                content = await r.json()
                joke = content["value"]
                joke_text = joke["joke"]
                categories = joke["categories"]

                embed = discord.Embed(title="Chuck Norris")
                embed.description = joke_text
                embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Chuck_Norris_May_"
                                        "2015.jpg/220px-Chuck_Norris_May_2015.jpg")
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

    @commands.command(name="nocontext", aliases=["ooc"])
    @commands.cooldown(1, 8, commands.BucketType.user)
    async def out_of_context(self, ctx, limit=500):
        """Picks a random message from the channel, out-of-context."""
        limit = max(min(limit, 2000), 0)

        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.message.delete()

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
