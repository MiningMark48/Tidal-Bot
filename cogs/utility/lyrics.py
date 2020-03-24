import typing

import discord
import requests
from bs4 import BeautifulSoup as bs
from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lyric_messages = []
        self.lyric_pages = []

        self.def_embed = discord.Embed(title="")

    # noinspection PyBroadException
    @commands.command(aliases=['cf', 'curse'])
    @commands.cooldown(1, 3.5)
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

                r = requests.get(base_url, params=payload, timeout=2)
                content = r.content
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

                max_chars = 1800
                self.lyric_pages = [(lyrics[i:i+max_chars]) for i in range(0, len(lyrics), max_chars)]

                embed = discord.Embed(title=page_title, url=s_r.url)
                embed.description = f'{lyrics[:max_chars]}{"..." if len(lyrics) > max_chars else ""}'
                embed.set_footer(text="Fetched from SongLyrics.com")

                self.def_embed = embed

                msg = await ctx.send(embed=embed)

                await msg.add_reaction("⬅️")
                await msg.add_reaction("➡️")
                self.lyric_messages.append(msg.id)

            except IndexError or requests.exceptions.ConnectTimeout:
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
                for reac in rmsg.reactions:
                    if not user == self.bot.user:
                        await reac.remove(user)

                        embed = self.def_embed
                        embed.description = self.lyric_pages[1]
                        await rmsg.edit(embed=embed)

                        # self.user_answers[user.id] = reaction_emoji

        except discord.errors.NotFound:
            pass


def setup(bot):
    bot.add_cog(Fun(bot))
