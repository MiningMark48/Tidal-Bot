import asyncio
import random

from discord.ext import commands

from util.decorators import delete_original


class BJMessage:
    def __init__(self, description, dealer_cards, player_cards, game_owner):
        self.title = "Blackjack"
        self.description = description
        self.field_dealer = dealer_cards
        self.field_player = player_cards
        self.game_owner = game_owner

    def set_description(self, text: str):
        self.description = text

    def set_dealer_field(self, text: str):
        self.field_dealer = text

    def set_player_field(self, text: str):
        self.field_player = text

    def set_game_owner(self, text: str):
        self.game_owner = text

    def get_message(self):
        message = f"__**{self.title}**__\n" \
                  f"{self.description}\n\n" \
                  f"**Dealer:** {self.field_dealer}\n" \
                  f"**Player:** {self.field_player}\n\n" \
                  f"*{self.game_owner}'s Game*"

        return str(message)


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.new_game = []

    @commands.command(name="blackjack", aliases=["21", "bj"])
    @delete_original()
    async def blackjack(self, ctx):
        """Play a (modified) game of blackjack, simplistic-ly."""

        def check(m, u):
            return u.id == ctx.author.id

        # print(BJMessage("D", "De", "Pl", "Fo").get_message())

        # Hand Pointing Down Emoji
        emoji_hit = "\N{WHITE DOWN POINTING BACKHAND INDEX}"
        # Hand Splayed Emoji
        emoji_stay = "\N{RAISED HAND WITH FINGERS SPLAYED}"
        emoji_clap = "\N{CLAPPING HANDS SIGN}"  # Clapping Hands Emoji

        # cards = list(range(1, 11))
        cards = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]
        cards_dealer = random.sample(cards, 2)
        cards_player = random.sample(cards, 2)

        # embed = discord.Embed(title="Blackjack", color=0x076324)
        # embed.set_footer(text=f"{ctx.author.display_name}'s game")
        # embed.add_field(name="Dealer", value=f"{str(cards_dealer[0])}  ?")
        # embed.add_field(name="Player",
        #                 value=f"{'  '.join(str(c) for c in cards_player)} ({sum(cards_player)})")

        embed = BJMessage(description="Loading...", dealer_cards=f"{str(cards_dealer[0])}  ?",
                          player_cards=f"{'  '.join(str(c) for c in cards_player)} ({sum(cards_player)})",
                          game_owner=ctx.author.display_name)

        # await ctx.send("**Note:** This may be a little slow to respond at the moment due to message edits.\nWorking "
        #                "on a fix", delete_after=10)
        msg = await ctx.send(embed.get_message())

        async def play():
            cards_player_sum = sum(cards_player)
            if cards_player_sum == 21:  # Blackjack
                # embed.description = f"Blackjack! You win! {emoji_contentclap}"
                # embed.set_field_at(0, name="Dealer",
                #                    value=f"{'  '.join(str(c) for c in cards_dealer)} ({sum(cards_dealer)})")

                embed.set_description(f"Blackjack! You win! {emoji_clap}")
                embed.set_dealer_field(f"{'  '.join(str(c) for c in cards_dealer)} ({sum(cards_dealer)})")

                await msg.edit(content=embed.get_message())
                await msg.clear_reactions()
            elif sum(cards_player) > 21:  # Bust
                # embed.description = "Bust, dealer wins."
                # embed.set_field_at(0, name="Dealer",
                #                    value=f"{'  '.join(str(c) for c in cards_dealer)} ({sum(cards_dealer)})")

                embed.set_description("Bust, dealer wins.")
                embed.set_dealer_field(f"{'  '.join(str(c) for c in cards_dealer)} ({sum(cards_dealer)})")

                await msg.edit(content=embed.get_message())
                await msg.clear_reactions()
            else:  # Hit/Stay
                # embed.description = f"Hit {emoji_hit} or stay {emoji_stay}?"

                embed.set_description(f"Hit {emoji_hit} or stay {emoji_stay}?")

                await msg.edit(content=embed.get_message())
                await msg.add_reaction(emoji_hit)
                await msg.add_reaction(emoji_stay)

                wf_react, wf_user = await self.bot.wait_for('reaction_add', check=check, timeout=15)
                wf_react = str(wf_react.emoji)

                if wf_react == emoji_hit:
                    cards_player.append(random.choice(cards))
                    # embed.set_field_at(1, name="Player",
                    #                    value=f"{'  '.join(str(c) for c in cards_player)} ({sum(cards_player)})")

                    embed.set_player_field(f"{'  '.join(str(c) for c in cards_player)} ({sum(cards_player)})")

                    await msg.edit(content=embed.get_message())

                    await msg.remove_reaction(emoji_hit, wf_user)
                    await play()
                elif wf_react == emoji_stay:
                    cards_player_sum = sum(cards_player)

                    async def card_dealer_draw():  # Dealer keeps drawing until 17 or higher
                        cards_dealer_sum = sum(cards_dealer)

                        if cards_dealer_sum < 17:
                            cards_dealer.append(random.choice(cards))
                            # embed.set_field_at(0, name="Dealer",
                            #                value=f"{'  '.join(str(c) for c in cards_dealer)} ({sum(cards_dealer)})")

                            embed.set_dealer_field(f"{'  '.join(str(c) for c in cards_dealer)} ({sum(cards_dealer)})")

                            await msg.edit(content=embed.get_message())

                            await asyncio.sleep(1)
                            await card_dealer_draw()
                        else:
                            if cards_player_sum > cards_dealer_sum or cards_dealer_sum > 21:
                                embed.set_description(f"Player wins! {emoji_clap}")
                            elif cards_player_sum < cards_dealer_sum or cards_dealer_sum == 21:
                                embed.set_description("Dealer wins.")
                            else:
                                embed.set_description("It's a push, you both win!")

                    await card_dealer_draw()

                    # embed.set_field_at(0, name="Dealer",
                    #                    value=f"{'  '.join(str(c) for c in cards_dealer)} ({sum(cards_dealer)})")

                    embed.set_dealer_field(f"{'  '.join(str(c) for c in cards_dealer)} ({sum(cards_dealer)})")

                    await msg.edit(content=embed.get_message())
                    await msg.clear_reactions()

                else:
                    await play()

        await asyncio.sleep(2)
        await play()

        # self.new_game.append(msg.id)
        # await msg.add_reaction("🔁")

    # @commands.Cog.listener("on_raw_reaction_add")
    # async def on_raw_reaction_add(self, payload):
    #     guild = self.bot.get_guild(payload.guild_id)
    #     channel = guild.get_channel(payload.channel_id)
    #     rmsg = await channel.fetch_message(payload.message_id)

    #     if rmsg.id in self.new_game:
    #         reaction_emoji = str(payload.emoji)
    #         user = self.bot.get_user(payload.user_id)
    #         if reaction_emoji == '🔁':
    #             if not user == self.bot.user:
    #                 ctx = await self.bot.get_context(rmsg)
    #                 cmd = self.bot.get_command("blackjack")
    #                 self.new_game.remove(rmsg.id)
    #                 await rmsg.clear_reactions()
    #                 await ctx.invoke(cmd)


def setup(bot):
    bot.add_cog(Fun(bot))
