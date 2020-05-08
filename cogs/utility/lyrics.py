import typing

import aiohttp
import discord
import requests
from bs4 import BeautifulSoup as bs
from discord.ext import commands


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lyric_messages = []
        self.lyric_pages = {}
        self.page_index = {}

        self.def_embed = {}

    # noinspection PyBroadException
    @commands.command(aliases=['lyric', 'lyr'])
    @commands.cooldown(1, 10)
    async def lyrics(self, ctx, song: str, author: typing.Optional[str]):
        """
        Search for lyrics for a song
        """
        async with ctx.typing():
            try:
                if not author:
                    author = ""
                song = song.replace(" ", "+")
                author = author.replace(" ", "+")
                query = f"{song} {author}"

                base_url = f"http://www.songlyrics.com/index.php"
                payload = {"section": "search", "searchW": query, "submit": "Search"}

                async with aiohttp.ClientSession() as session:
                    async with session.get(base_url, params=payload) as r:
                        content = await r.content.read()
                        soup = bs(content, 'html.parser')

                        search_results = soup.find_all("div", class_="serpresult")
                        top_result = search_results[0]

                        link_elm = top_result.find_all("a")[0]
                        song_link = link_elm['href']

                        s_r = requests.get(song_link, timeout=1)
                        s_content = s_r.content
                        s_soup = bs(s_content, 'html.parser')

                        lyrics = s_soup.find_all(id="songLyricsDiv")[0].get_text()
                        page_title_div = s_soup.find_all("div", class_="pagetitle")[0]
                        page_title = page_title_div.find_all("h1")[0].get_text()

                        max_chars = 700
                        lyric_pages = [(lyrics[i:i+max_chars]) for i in range(0, len(lyrics), max_chars)]
                        page_info = f'\n\n**Page:** 1/{len(lyric_pages)}'

                        embed = discord.Embed(title=page_title, url=s_r.url, color=0x657079)
                        embed.description = f'{lyrics[:max_chars]} {page_info if len(lyric_pages)>1 else ""}'
                        embed.set_footer(text="Fetched from SongLyrics.com")

                        msg = await ctx.send(embed=embed)

                        if len(lyric_pages) > 1:
                            if len(lyric_pages) > 2:
                                await msg.add_reaction("⏪")
                            await msg.add_reaction("◀")
                            await msg.add_reaction("▶")
                            if len(lyric_pages) > 2:
                                await msg.add_reaction("⏩")

                            self.lyric_messages.append(msg.id)
                            self.lyric_pages.update({msg.id: lyric_pages})
                            self.page_index.update({msg.id: 0})
                            self.def_embed.update({msg.id: embed})

            except IndexError or requests.exceptions.ConnectTimeout or requests.exceptions.ReadTimeout:
                await ctx.send("No search results found!")
            except Exception as e:
                await ctx.send(f"An error occurred!\n`{e}`")

    @commands.Cog.listener("on_raw_reaction_add")
    async def on_raw_reaction_add(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        try:
            rmsg = await channel.fetch_message(payload.message_id)
            if rmsg.id in self.lyric_messages:
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
                        p_index.update({mid: len(self.lyric_pages.get(mid))-1})
                        update = True

                    if update:
                        p_index.update({mid: max(min(p_index.get(mid), len(self.lyric_pages.get(mid))-1), 0)})
                        self.page_index.update(p_index)

                        page_info = f'\n\n**Page:** {self.page_index.get(mid)+1}/{len(self.lyric_pages.get(mid))}'

                        e = self.def_embed.get(mid)

                        e.description = f'{self.lyric_pages.get(mid)[self.page_index.get(mid)]}' \
                                        f' {page_info if len(self.lyric_pages.get(mid))>1 else ""}'
                        await rmsg.edit(embed=e)
                        self.def_embed.update({mid: e})

                    for reac in rmsg.reactions:
                        await reac.remove(user)

        except discord.errors.NotFound:
            pass


def setup(bot):
    bot.add_cog(Utility(bot))
