import traceback
import sys
from discord.ext import commands
import discord

class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        ctx   : Context
        error : Exception"""

        if hasattr(ctx.command, 'on_error'):
            return
        
        ignored = (commands.CommandNotFound)
        error = getattr(error, 'original', error)
        
        if isinstance(error, ignored):
            return

        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send(f'`{ctx.command}` has been disabled.')

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.author.send(f'`{ctx.command}` can not be used in direct messages.')
            except:
                pass

        elif isinstance(error, commands.BadArgument):
            if ctx.command.qualified_name == 'tag list':
                return await ctx.send('I could not find that member. Please try again.')
            else:
                cmdhelp = ctx.command.help
                return await ctx.send(f'`{ctx.command}` received an invalid argument! '
                                      f'More info:\n```{ctx.prefix}{ctx.command} {ctx.command.signature}\n\n'
                                      f'{cmdhelp if cmdhelp else ""}```')
            
        elif isinstance(error, commands.MissingRequiredArgument):
            cmdhelp = ctx.command.help
            return await ctx.send(f'`{ctx.command}` is missing required arguments! '
                                  f'More info:\n```{ctx.prefix}{ctx.command} {ctx.command.signature}\n\n'
                                  f'{cmdhelp if cmdhelp else ""}```')

        elif isinstance(error, commands.NSFWChannelRequired):
            return await ctx.send(f'`{ctx.command}` can only be used in a NSFW channel!')

        elif isinstance(error, commands.MissingPermissions):
            return await ctx.send(error)

        # elif isinstance(error, commands.BadArgument):
        #     return await ctx.send(f'`{ctx.command}` received an invalid argument!')

        elif isinstance(error, commands.UserInputError):
            cmdhelp = ctx.command.help
            return await ctx.send(f'`{ctx.command}` is either missing or received an invalid argument! '
                                  f'More info:\n```{ctx.prefix}{ctx.command} {ctx.command.signature}\n\n'
                                  f'{cmdhelp if cmdhelp else ""}```')

        elif isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(f'`{ctx.command}`: {error}')

        elif isinstance(error, discord.errors.Forbidden):
            return await ctx.send(f'Bot does not have required permissions to use `{ctx.command}`.')
            
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
    
    # @commands.command(name='repeat', aliases=['mimic', 'copy'])
    # async def do_repeat(self, ctx, *, inp: str):
    #     await ctx.send(inp)

    # @do_repeat.error
    # async def do_repeat_handler(self, ctx, error):
    #     if isinstance(error, commands.MissingRequiredArgument):
    #         if error.param.name == 'inp':
    #             await ctx.send("You forgot to give me input to repeat!")
                

def setup(bot):
    bot.add_cog(Errors(bot))
