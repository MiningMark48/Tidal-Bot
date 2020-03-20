import asyncio
import datetime
import random
import time
from datetime import datetime as dt

import discord
from discord.ext import commands
from pytz import timezone as tz

start_time = time.time()


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def giveaway(self, ctx, time: int, *, giveaway: str):
        """
        Create a giveaway for users to join.

        Usage: giveaway <time (minutes)> <Giveaway Name>
        Ex: giveaway 60 Free Hugs

        Note: Time must be between 1 minute and 60 minutes.
        """

        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

        reaction_emoji = "🎉"

        if 0 < time <= 60:
            end_time = dt.now(tz=tz("US/Eastern")) + datetime.timedelta(minutes=time)
            # timezone = strftime("%Z", gmtime())

            embed = discord.Embed(title=f"{reaction_emoji} Giveaway {reaction_emoji}", color=0xfc68a6)
            embed.description = f'**{giveaway}**\n\n' \
                                f'React with {reaction_emoji} to enter!\n\n' \
                                f'Ends at: \n{end_time.strftime("%I:%M:%S %p %Z")}'
            embed.set_footer(text=f'Created by {ctx.author.display_name}')

            msg = await ctx.send(embed=embed)
            await msg.add_reaction(reaction_emoji)

            await asyncio.sleep(time * 60)

            entries = []

            r_msg = await ctx.channel.fetch_message(msg.id)

            for reac in r_msg.reactions:
                if reac.emoji == reaction_emoji:
                    async for usr in reac.users():
                        if not usr.bot:
                            entries.append(usr)

            await r_msg.clear_reactions()

            if entries:
                embed.description = f"**{giveaway}**\n\n" \
                                    f"Giveaway Over!\n\n" \
                                    f"Drawing winner..."
                await r_msg.edit(embed=embed)
                await asyncio.sleep(1)

                winning_entry = random.choice(entries)
                embed.description = f"**{giveaway}**\n\n" \
                                    f"Giveaway Over!\n\n" \
                                    f"Out of {len(entries)} entr{'y' if len(entries) == 1 else 'ies'},\n" \
                                    f"{winning_entry.mention} is the winner!"
                await r_msg.edit(embed=embed)

                await ctx.author.send(f'Your giveaway `{giveaway}` just ended in {ctx.guild.name}. '
                                      f'{winning_entry.mention} was the winner.')
                await winning_entry.send(f'{winning_entry.mention}, you won the giveaway `{giveaway}` '
                                         f'in {ctx.guild.name}!')

            else:
                embed.description = f"Giveaway Over!\n\n" \
                                    f"Nobody entered the giveaway."
                await r_msg.edit(embed=embed)

                await ctx.author.send(f'Your giveaway `{giveaway}` just ended in {ctx.guild.name}. '
                                      f'There were no entries, so nobody won.')


def setup(bot):
    bot.add_cog(Utility(bot))
