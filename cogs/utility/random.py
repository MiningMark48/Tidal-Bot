import random
import string

import discord
from faker import Faker

from discord.ext import commands


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="coinflip", aliases=["coin", "flipcoin"])
    async def coin_flip(self, ctx):
        """Flip a coin!"""
        flip = random.randint(0, 1)
        await ctx.send(f':moneybag: You flipped a coin and got **{"heads" if flip == 0 else "tails"}**! :moneybag:')

    @commands.command(name="diceroll", aliases=["dice", "rolldice"])
    async def dice_roll(self, ctx, amt=1):
        """Roll a dice!"""
        if 0 < amt <= 25:
            roll = ', '.join(str(random.randint(1, 6)) for x in range(amt))
            await ctx.send(f':game_die: You rolled a die and got... **{roll}**! :game_die:')
        else:
            await ctx.send('Amount must be between **0** and **25**!')

    @commands.command(name="randcard", aliases=["randcards", "card", "cards"])
    async def rand_card(self, ctx, amt=1):
        """Draw a random card from a deck"""

        amt = max(min(amt, 52), 1)

        suits = ["Spades", "Clubs", "Hearts", "Diamonds"]
        nums = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]

        cards = []

        def draw_card():
            num = random.choice(nums)
            suit = random.choice(suits)
            card = f"{num} of {suit}"

            if card in cards:
                draw_card()
            else:
                cards.append(card)

        for i in range(0, amt):
            draw_card()

        message = ', '.join(card for card in cards)
        await ctx.send(f"{ctx.author.mention}, here ya go!\n{message}")

    @commands.command(name="randchoice", aliases=["randc", "randomc"])
    async def rand_choice(self, ctx, *choices: str):
        """Get a random choice from a list of provided choices"""
        if len(choices) < 2:
            await ctx.send("You must have at least **2** choices.")
            return

        choice = random.choice(choices)
        await ctx.send(f"Your random choice is `{choice}`!")

    @commands.command(name="randnum", aliases=["rand", "random"])
    async def rand_num(self, ctx, min: int, max: int, amt=1):
        """Get a random number between two values"""
        if 0 < amt <= 25:
            roll = ', '.join(str(random.randint(min, max)) for x in range(amt))
            await ctx.send(f'Your random number{"s are" if amt > 1 else " is"}... **{roll}**!')
        else:
            await ctx.send('Amount must be between **0** and **25**!')

    @commands.command(name="randperson", aliases=["fakeperson"])
    async def rand_person(self, ctx):
        """Generate a fake person profile"""
        fake = Faker("en_US")

        profile = fake.profile(fields=None, sex=None)

        name = profile["name"]
        address = profile["address"]
        sex = "Male" if profile["sex"] == "M" else "Female"
        birthday = profile["birthdate"]
        # phone = fake.phone_number()
        ssn = profile["ssn"]
        email = profile["mail"]
        website = random.choice(profile["website"])
        username = profile["username"]
        company = profile["company"]
        job = profile["job"]
        license_plate = fake.license_plate()

        embed = discord.Embed(title=name)
        embed.add_field(name="Address", value=address, inline=False)
        embed.add_field(name="Sex", value=sex)
        embed.add_field(name="Birthday", value=birthday)
        # embed.add_field(name="Phone", value=phone)
        embed.add_field(name="SSN", value=ssn)
        embed.add_field(name="Email", value=email)
        embed.add_field(name="Website", value=website)
        embed.add_field(name="Username", value=username)
        embed.add_field(name="Company", value=company)
        embed.add_field(name="Job", value=job)
        embed.add_field(name="License Plate", value=license_plate)

        embed.set_footer(text="Disclaimer: The profile generated is random data.")
        await ctx.send(embed=embed)

    @commands.command(name="randtext", aliases=["lorem", "loremipsum"])
    async def rand_text(self, ctx, max_chars=500):
        """Generate random text."""

        max_chars = max(min(max_chars, 1900), 25)

        fake = Faker("en_US")

        text = fake.text(max_nb_chars=max_chars, ext_word_list=None)
        text = text.replace("\n", " ")

        await ctx.send(f"```{text}```")


def setup(bot):
    bot.add_cog(Utility(bot))

