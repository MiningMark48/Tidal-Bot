import discord
from discord.ext import commands

import util.servconf as sc


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.flag_amts = {}
        self.flag_modes = {}

    @commands.Cog.listener("on_ready")
    async def on_ready(self):
        self.update_flag_amts()
        self.update_flag_modes()

    @commands.Cog.listener("on_raw_reaction_add")
    async def on_raw_reaction_add(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        rmsg = await channel.fetch_message(payload.message_id)
        reaction_emoji = str(payload.emoji)
        # user = self.bot.get_user(payload.user_id)
        for reac in rmsg.reactions:
            if reaction_emoji == '🚫':
                amt = reac.count
                if self.flag_modes.get(str(guild.id)):
                    del_amt = self.flag_amts.get(str(guild.id))
                else:
                    del_amt = self.calc_prop_members(guild.members, self.flag_amts.get(str(guild.id)))

                if del_amt == 0:
                    return
                if amt >= del_amt:
                    users = await reac.users().flatten()
                    ctx = await self.bot.get_context(rmsg)

                    await self.log_action(ctx, users)
                    await rmsg.delete()
                    await channel.send('Message deleted.', delete_after=10)

    @commands.group(name="flagging", aliases=["flag"])
    async def flagging(self, ctx):
        """Flagging allows members of a server to flag a message they find inappropriate for deletion."""
        pass

    @flagging.command(name="help")
    async def flag_help(self, ctx):
        """Get help with flagging"""

        info = f"{ctx.command.help}\n\n" \
               f"The reaction for flagging is NO_ENTRY_SIGN (🚫).\n" \
               f"The default required amount of reactions is **0** (disabled), and uses **set** mode.\n" \
               f"This value can be changed with `setflagamt` and the mode can be changed with `setflagmode`\n" \
               f"Use the `getflagamt` command to see the currently set value.\n" \
               f"Use the `getflagmode` command to see the currently set mode.\n\n" \
               f"Setting the value to **0** will disable flagging.\n" \
               f"Flagging value has a maximum of **100**.\n\n" \
               f"**Modes:** Set is a specific amount, proportional is a percentage of members\n\n" \
               f"Do `{ctx.prefix}help flagging` for a list of commands."

        await ctx.send(info)

    @flagging.command(name="getamt")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def get_flag_amt(self, ctx):
        """Get the current flag amount for message flagging"""

        mode = sc.get_v(str(ctx.guild.id), "flag_mode_set")
        if mode is None:
            mode = True

        amt = sc.get_v(str(ctx.guild.id), "flag_amt")
        if not amt:
            amt = 0
        del_amt = self.calc_prop_members(ctx.guild.members, amt)
        await ctx.send(f'The flag amount is `{amt}{"%` of server members" if not mode else "`"}.'
                       f'\n\n{"**Currently:** " + str(del_amt) if not mode else ""}')

    @flagging.command(name="setamt")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def set_flag_amt(self, ctx, amt: int):
        """Change the flag amount for message flagging"""

        amt = max(0, min(amt, 100))

        sc.set_kv(str(ctx.guild.id), "flag_amt", amt)
        self.update_flag_amts()
        await ctx.send(f'Changed the flag amount to `{amt}`.')

    @flagging.command(name="setmode")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def set_flag_mode(self, ctx, mode: str):
        """
        Change the flag mode for message flagging

        Modes: Set (s), Proportional (p)

        Set is a specific amount, proportional is a percentage of members.
        """

        mode = mode.lower()
        if mode in ["set", "s"]:
            sc.set_kv(str(ctx.guild.id), "flag_mode_set", True)
            self.update_flag_modes()
            await ctx.send("Set flag mode to `Set`")
        elif mode in ["proportional", "p"]:
            sc.set_kv(str(ctx.guild.id), "flag_mode_set", False)
            self.update_flag_modes()
            await ctx.send("Set flag mode to `Proportional`")
        else:
            await ctx.send("Invalid mode.")

    @flagging.command(name="getmode")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def get_flag_mode(self, ctx):
        """Get the flag mode for message flagging"""

        mode_set = sc.get_v(str(ctx.guild.id), "flag_mode_set")
        mode = "Set" if mode_set else "Proportional"

        if mode_set is None:
            mode = "set"

        await ctx.send(f'The flag mode is `{mode}`.')

    def update_flag_amts(self):
        cfg_data = sc.get_data()
        for id in cfg_data:
            try:
                amt = cfg_data[id]['flag_amt']
            except KeyError:
                amt = 0
            self.flag_amts[id] = amt

    def update_flag_modes(self):
        cfg_data = sc.get_data()
        for id in cfg_data:
            try:
                mode = cfg_data[id]['flag_mode_set']
            except KeyError:
                mode = True
            self.flag_modes[id] = mode

    @staticmethod
    async def log_action(ctx, reactors):
        try:
            channel = discord.utils.find(
                lambda c: (isinstance(c, discord.TextChannel) and "[tb-log]" in (c.topic if c.topic else "")),
                ctx.guild.channels)
            if channel:
                embed = discord.Embed(title="Flagged Message", color=0xff0000)
                embed.add_field(name="Flagged by", value=', '.join(r.mention for r in reactors))
                embed.add_field(name="Executed at", value=str(ctx.message.created_at)[:19])
                # embed.add_field(name="Message Link", value=f'[Click Here]({ctx.message.jump_url})')
                message_content = ctx.message.content
                embed.add_field(name="Full Message",
                                value=f'{message_content[:100]}...' if len(message_content) > 100 else message_content,
                                inline=False)
                await channel.send(embed=embed)
        except discord.errors.HTTPException:
            pass

    @staticmethod
    def calc_prop_members(members, amt):
        return round(len(members) * (amt / 100))


def setup(bot):
    bot.add_cog(Moderation(bot))
