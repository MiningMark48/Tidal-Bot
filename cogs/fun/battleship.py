import random

from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    # @commands.cooldown(1, 15, commands.BucketType.user)
    async def battleship(self, ctx):
        """Battleship - WIP"""
        await ctx.send(self.gen_board())

    # noinspection PyTypeChecker
    def gen_board(self):
        base = 10
        # side = base * base
        ships = [5, 4, 3, 3, 2]
        random.shuffle(ships)

        board = [[0 for c in range(base)] for r in range(base)]

        for ship in ships:
            r_row = board[random.randint(0, len(board)-1)]
            r_row[random.randint(0, len(r_row)-1)] = ship

        # cp_board = []
        # for row in board:
        #     cp_board.append(row.copy())

        for i in range(len(board)):
            for j in range(len(board[i])):
                ship = board[i][j]
                # print(f'({j+1}, {i+1}) - {ship}')
                if isinstance(ship, int) and int(ship) > 0:
                    board = self.place_ship(board, (i, j), ship)
                    # print("ran")
        # board = cp_board

        msg = "```"
        for row in board:
            for num in row:
                msg += f' {num if not num == 0 else "|"} '
            msg += "\n"
        msg += "```"

        return msg

    @staticmethod
    def get_rand_dir():
        directions = ["u", "d", "l", "r"]
        return random.choice(directions)

    def place_ship(self, board, pos, ship):
        cp_board = []
        for row in board:
            cp_board.append(row.copy())
        direction = self.get_rand_dir()
        r = pos[0]
        c = pos[1]

        # direction = "l"

        board[r][c] = str(ship)
        row_val = 0
        col_val = 0
        do_place = []
        for n in range(1, ship):
            if direction == "l":
                row_val = 0
                col_val = -1
            elif direction == "r":
                row_val = 0
                col_val = 1
            elif direction == "u":
                row_val = -1
                col_val = 0
            elif direction == "d":
                row_val = 1
                col_val = 0

            # print(f'{ship} - ({abs(r + (n * row_val))}, {abs(c + (n * col_val))})')
            try:
                do_place.append(self.can_place(cp_board[abs(r + (n * row_val))][abs(c + (n * col_val))]))
            except IndexError:
                self.place_ship(cp_board, pos, ship)
                break
        if do_place:
            do_place.pop(0)
        if all(do_place):
            for i in range(1, ship):
                try:
                    cp_board[abs(r + (i * row_val))][abs(c + (i * col_val))] = str(ship)
                except IndexError:
                    self.place_ship(cp_board, pos, ship)
                    break
        else:
            self.place_ship(cp_board, pos, ship)

        return cp_board

    @staticmethod
    def can_place(num):
        return num == 0


def setup(bot):
    bot.add_cog(Fun(bot))
