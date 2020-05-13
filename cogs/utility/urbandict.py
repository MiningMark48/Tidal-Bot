import aiohttp

import discord
from bs4 import BeautifulSoup as bs
from discord.ext import commands


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
                base_url = f"https://www.urbandictionary.com/define.php?term={query}"

                async with aiohttp.ClientSession() as session:
                    async with session.get(base_url) as r:
                        content = await r.content.read()

                        soup = bs(content, 'html.parser')

                        for br in soup.find_all("br"):
                            br.replace_with("\n")

                        div_content = soup.find_all(id="content")[0]

                        def_panel_list = div_content.find_all("div", class_="def-panel")
                        dict_pages = []
                        for index in range(0, len(def_panel_list)-1):
                            def_panel = def_panel_list[index]
                            def_header = def_panel.find_all("div", class_="def-header")[0]
                            word = def_header.find_all("a", class_="word")[0]
                            word_text = str(word.get_text()).capitalize()
                            meaning = def_panel.find_all("div", class_="meaning")[0]
                            meaning_text = meaning.get_text()
                            dict_pages.append((word_text, meaning_text))

                        page_info = f'\n\n**Page:** 1/{len(dict_pages)}'
                        w, m = dict_pages[0]
                        embed = discord.Embed(title=w, url=str(r.url), color=0x1d2439)
                        embed.description = f'{m[:1800]} {"..." if len(m) > 1800 else ""} ' \
                                            f'{page_info if len(page_info)>1 else ""}'
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
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        try:
            rmsg = await channel.fetch_message(payload.message_id)
            if rmsg.id in self.dict_messages:
                reaction_emoji = str(payload.emoji)
                user = self.bot.get_user(payload.user_id)
                if not user == self.bot.user:

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
                        p_index.update({mid: len(self.dict_pages.get(mid))-1})
                        update = True

                    if update:
                        p_index.update({mid: max(min(p_index.get(mid), len(self.dict_pages.get(mid)) - 1), 0)})
                        self.page_index.update(p_index)

                        page_info = f'\n\n**Page:** {self.page_index.get(mid)+1}/{len(self.dict_pages.get(mid))}'

                        e = self.def_embed.get(mid)

                        w, m = self.dict_pages.get(mid)[self.page_index.get(mid)]

                        e.title = w
                        e.description = f'{m[:1800]}{"..." if len(m) > 1800 else ""} ' \
                                        f'{page_info if len(self.dict_pages.get(mid))>1 else ""}'

                        await rmsg.edit(embed=e)
                        self.def_embed.update({mid: e})

                    for reac in rmsg.reactions:
                        await reac.remove(user)

        except discord.errors.NotFound:
            pass


def setup(bot):
    bot.add_cog(Utility(bot))
