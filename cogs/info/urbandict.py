from re import S
import aiohttp

import discord
from bs4 import BeautifulSoup as bs
from discord.ext import commands

from util.messages import MessagesUtil


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.messages_util = MessagesUtil(bot)

        self.dict_messages = []
        self.dict_pages = {}
        self.page_index = {}

        self.def_embed = {}

    # noinspection PyBroadException
    @commands.command(aliases=['urbandictionary', 'urbandict'])
    @commands.cooldown(1, 3.5)
    @commands.is_nsfw()
    async def urban(self, ctx, *, query: str):
        """
        Define a word from Urban Dictionary
        """

        async with ctx.typing():
            try:
                # query = html.escape(query)
                query = query.replace(" ", "+")
                base_url = "https://api.urbandictionary.com/v0/define"
                payload = {'term': query}

                async with aiohttp.ClientSession() as session:
                    async with session.get(base_url, params=payload) as r:
                        content = await r.json()

                        def_list = content['list']
                        dict_pages = []
                        for _def in def_list:
                            word_text = _def['word']
                            meaning_text = str(_def['definition']).replace("[", "").replace("]", "")
                            example_text = str(_def['example']).replace("[", "").replace("]", "")
                            dict_pages.append((word_text, meaning_text, example_text))

                        page_info = f'\n\n**Page:** 1/{len(dict_pages)}'
                        w, m, ex = dict_pages[0]
                        embed = discord.Embed(title=w, color=0x1d2439)
                        embed.description = f'{m[:1800]} {"..." if len(m) > 1800 else ""} ' \
                                            f'\n\n**Example:** {ex[:100]} {"..." if len(ex) > 100 else ""}' \
                                            f'{page_info if len(page_info) > 1 else ""}'
                        embed.set_footer(text="Fetched from Urban Dictionary")

                        msg = await ctx.send(embed=embed)

                        if len(dict_pages) > 1:
                            if len(dict_pages) > 2:
                                await msg.add_reaction("⏪")
                            await msg.add_reaction("◀")
                            await msg.add_reaction("▶")
                            if len(dict_pages) > 2:
                                await msg.add_reaction("⏩")

                        self.dict_messages.append(msg.id)
                        self.dict_pages.update({msg.id: dict_pages})
                        self.page_index.update({msg.id: 0})
                        self.def_embed.update({msg.id: embed})

            except IndexError:
                await ctx.send("No search results found!")
            except Exception as e:
                await ctx.send(f"An error occurred!\n`{e}`")

    @commands.Cog.listener("on_raw_reaction_add")
    async def on_raw_reaction_add(self, payload):
        user = self.bot.get_user(payload.user_id)

        if user == self.bot.user:
            return

        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        try:
            # rmsg = await channel.fetch_message(payload.message_id)
            rmsg = await self.messages_util.get_message(channel, payload.message_id)
            if rmsg.id in self.dict_messages:
                reaction_emoji = str(payload.emoji)

                mid = rmsg.id
                p_index = {mid: self.page_index.get(mid)}
                update = False
                if reaction_emoji == "▶":
                    p_index.update({mid: p_index.get(mid) + 1})
                    update = True
                elif reaction_emoji == "◀":
                    p_index.update({mid: p_index.get(mid) - 1})
                    update = True
                elif reaction_emoji == "⏪":
                    p_index.update({mid: 0})
                    update = True
                elif reaction_emoji == "⏩":
                    p_index.update({mid: len(self.dict_pages.get(mid)) - 1})
                    update = True

                if update:
                    p_index.update({mid: max(min(p_index.get(mid), len(self.dict_pages.get(mid)) - 1), 0)})
                    self.page_index.update(p_index)

                    page_info = f'\n\n**Page:** {self.page_index.get(mid) + 1}/{len(self.dict_pages.get(mid))}'

                    e = self.def_embed.get(mid)

                    w, m, ex = self.dict_pages.get(mid)[self.page_index.get(mid)]

                    e.title = w
                    e.description = f'{m[:1800]}{"..." if len(m) > 1800 else ""} ' \
                                    f'\n\n**Example:** {ex[:100]} {"..." if len(ex) > 100 else ""}' \
                                    f'{page_info if len(self.dict_pages.get(mid)) > 1 else ""}'

                    await rmsg.edit(embed=e)
                    self.def_embed.update({mid: e})

                for reac in rmsg.reactions:
                    await reac.remove(user)

        except discord.errors.NotFound:
            pass


def setup(bot):
    bot.add_cog(Info(bot))
