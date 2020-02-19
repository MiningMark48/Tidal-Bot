import discord

def get_default_embed(**kwargs):
    embed = discord.Embed(**kwargs, color=0x00ff0000)
    return embed