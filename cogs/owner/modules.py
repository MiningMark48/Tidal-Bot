from discord.ext import commands

from util.extensions import get_extensions
from util.logger import Logger


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, cog: str):
        """Load a cog"""
        try:
            self.bot.load_extension(f"cogs.{cog}")
        except commands.ExtensionError as e:
            await ctx.send(f"**Error:** `{e}`")
            Logger.fatal(f"Tried to load: {e}")
        else:
            await ctx.send(f"**{cog}** loaded.")
            Logger.info(f"{cog} loaded.")

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, cog: str, create_backup=False):
        """Reload a specific cog"""

        if create_backup:
            cmd = self.bot.get_command("createbackup")
            await ctx.invoke(cmd)

        await ctx.send(f"Reload of `{cog}` beginning...")

        try:
            self.bot.reload_extension(f"cogs.{cog}")
        except Exception as e:
            Logger.fatal(f"Error reloading : \n\t{e}")
            await ctx.send(f"Error reloading : `{e}`")
        else:
            Logger.info(f"{ctx.author} reloaded {cog}")
            await ctx.send(f"Reloaded `{cog}`.")

    @commands.command(name="reloadall")
    @commands.is_owner()
    async def reload_all(self, ctx, create_backup=False):
        """Reload all cogs"""

        if create_backup:
            cmd = self.bot.get_command("createbackup")
            await ctx.invoke(cmd)

        await ctx.send("Reload beginning...")

        for extension in get_extensions():
            try:
                self.bot.reload_extension(f"cogs.{extension}")
                Logger.info(f"Reloaded {extension}")
            except Exception as e:
                Logger.fatal(f"Error reloading : \n\t{e}")
                await ctx.send(f"Error reloading : `{e}`")

        await ctx.send("Reloaded all cogs.")
        Logger.info(f"{ctx.author} reloaded all cogs")

    # noinspection PyBroadException
    @commands.command(name="reloadmusic")
    @commands.is_owner()
    async def reload_music(self, ctx):
        """Reload the music module"""
        await ctx.send("Reloading music...")
        try:
            self.bot.reload_extension("cogs.music")
            await ctx.send("Music reloaded.")
        except Exception as e:
            print(e)
            await ctx.send("Error reloading!")

        Logger.info(f"{ctx.author} reloaded music")

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, cog: str):
        """Unload a cog"""
        try:
            self.bot.unload_extension(f"cogs.{cog}")
        except commands.ExtensionError as e:
            await ctx.send(f"**Error:** `{e}`")
            Logger.fatal(f"Tried to unload: {e}")
        else:
            await ctx.send(f"**{cog}** unloaded.")
            Logger.info(f"{cog} unloaded.")


def setup(bot):
    bot.add_cog(Owner(bot))
