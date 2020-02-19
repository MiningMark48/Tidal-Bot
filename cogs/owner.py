import discord
import random
import os
import sys
import util.userconf as uc
from discord.ext import commands
# import cogs.checks as cks

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def botannounce(self, ctx, *, msg: str):

        def check(m):
            return m.author.id == ctx.author.id

        msg_c = await ctx.send("Are you sure? Reply with **Yes** to confirm.")
        msg_wf = await self.bot.wait_for('message', check=check, timeout=15)

        if msg_wf.content == "Yes":
            embed = discord.Embed(title="Announcement", color=0xffffff)
            embed.description = f'{msg}\n\n\nYou received this message because you\'re subscribed as follower. Do `{ctx.prefix}follow` to unsubscribe.'
            embed.set_footer(text=f'Sent by {ctx.author.name}#{ctx.author.discriminator}')

            users = uc.get_all_if_equals("follow_mode", True)
            sent = False
            for u in users:
                user = self.bot.get_user(int(u))
                if user:
                    await user.send(embed=embed)
                    sent = True
            if sent:
                await ctx.send(f'Message sent!\n```{msg}```')
            else:
                await ctx.send(f'Message wasn\'t sent.')
        else:
            await msg_c.delete()
            await ctx.send("Aborted!")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def changepresence(self, ctx, *, presence: str):
        await self.bot.change_presence(activity=discord.Activity(name=presence, type=discord.ActivityType.playing))
        await ctx.send(f"Changed presence to `{presence}`")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def getservers(self, ctx):
        # guilds = {}
        guilds = '\n'.join(f"{guild.name} ({guild.id})" for guild in self.bot.guilds)
        # for guild in self.bot.guilds:
        #     guilds[guild.id] = guild.name
        await ctx.send('Check your DMs!')
        await ctx.author.send(guilds)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def leaveserver(self, ctx, id: int):
        guild = self.bot.get_guild(id)
        await guild.leave()
        await ctx.send(f'Left **{guild.name}** (*{guild.id}*).')

    # @commands.command(hidden=True, aliases=["reload"])
    # @commands.is_owner()
    # async def restartbot(self, ctx):
    #     await ctx.send("Restarting bot...")
    #     print(f'Restarting bot...')
    #     await self.bot.logout()
    #     self.bot.run(self.bot.bot_token)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.send("Shutting down bot...")
        await self.bot.logout()

def setup(bot):
    bot.add_cog(Owner(bot))