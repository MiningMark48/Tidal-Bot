import discord

class MessagesUtil:

    def __init__(self, bot):
        self.bot = bot

    async def get_message(self, channel, message_id):
        found_message = discord.utils.find(lambda m: m.id == message_id, self.bot.cached_messages)

        if found_message:
            return found_message

        return await channel.fetch_message(message_id)
