import random
from discord.ext import commands
import random

from discord.ext import commands


# import cogs.checks as cks

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["ms", "mines"])
    async def minesweeper(self, ctx):
        """Create a minefield!"""
        columns = 10
        rows = 10
        bombs = random.randint(5, 10)

        grid = [[0 for num in range(columns)] for num in range(rows)]
        
        itr = 0
        while itr < bombs:
            x = random.randint(0, columns - 1)
            y = random.randint(0, rows - 1)
            if grid[y][x] == 0:
                grid[y][x] = 'B'
                itr += 1
            if grid[y][x] == 'B':
                pass

        pos_x = 0
        pos_y = 0
        while pos_x * pos_y < columns * rows and pos_y < rows:
            adj_sum = 0
            for (adj_y, adj_x) in [(0,1), (0,-1), (1,0), (-1,0), (1,1), (-1,1), (1,-1), (-1,-1)]:
                try:
                    if grid[adj_y + pos_y][adj_x + pos_x] == 'B' and adj_y + pos_y > -1 and adj_x + pos_x > -1:
                        adj_sum += 1
                except Exception:
                    pass
            if not grid[pos_y][pos_x] == 'B':
                grid[pos_y][pos_x] = adj_sum
            if pos_x == columns - 1:
                pos_x = 0
                pos_y += 1
            else:
                pos_x += 1

        sb = []
        for rws in grid:
            sb.append(''.join(map(str, rws)))
        sb = '\n'.join(sb)
        sb = sb.replace('0', '||:zero:||')
        sb = sb.replace('1', '||:one:||')
        sb = sb.replace('2', '||:two:||')
        sb = sb.replace('3', '||:three:||')
        sb = sb.replace('4', '||:four:||')
        sb = sb.replace('5', '||:five:||')
        sb = sb.replace('6', '||:six:||')
        sb = sb.replace('7', '||:seven:||')
        sb = sb.replace('8', '||:eight:||')
        sb = sb.replace('B', '||:bomb:||')
        final = f'{ctx.author.mention}, here\'s your game of Minesweeper!\n\n' \
                f'{sb}\n\n' \
                f'[{columns}x{rows} Grid - {bombs} Bombs]'

        await ctx.send(final)        

def setup(bot):
    bot.add_cog(Fun(bot))
