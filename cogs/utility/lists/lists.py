from discord.ext import commands

import cogs.utility.lists.listconf as lc


class Lists(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lists = {}

    @commands.Cog.listener("on_ready")
    async def on_ready(self):
        """Load JSON tags when ready"""
        self.lists = lc.get_data()

    @commands.command(name="listnew", aliases=["newlist"])
    @commands.cooldown(1, 5)
    async def list_new(self, ctx, *, list_name: str):
        """
        Create a new list.
        """
        if not str(ctx.author.id) in self.lists:
            self.lists.update({str(ctx.author.id): {}})

        if list_name in self.lists[str(ctx.author.id)]:
            await ctx.send("That list already exists!")
            return

        list_name = list_name.lower()
        self.lists[str(ctx.author.id)].update({list_name: []})
        lc.update_users(self.lists)
        lc.save_data()
        await ctx.send(f"Created new list `{list_name}`.")

    @commands.command(name="deletelist", aliases=["dellist", "listdelete"])
    @commands.cooldown(1, 5)
    async def list_delete(self, ctx, *, list_name: str):
        """
        Delete a list.
        """
        try:
            list_name = list_name.lower()
            self.lists[str(ctx.author.id)].pop(list_name)
            lc.update_users(self.lists)
            lc.save_data()
            await ctx.send(f"Deleted list `{list_name}`.")
        except KeyError:
            await ctx.send("Invalid list!")

    @commands.command(name="listslist", aliases=["listlists", "lists"])
    @commands.cooldown(1, 3)
    async def lists_list(self, ctx):
        """
        List current user lists.
        """
        try:
            user_lists = self.lists[str(ctx.author.id)]

            lists = f"{ctx.author.name}'s Lists\n\n"
            for t in sorted(user_lists):
                lists += f"- {t}\n"

            parts = [(lists[i:i + 750]) for i in range(0, len(lists), 750)]
            for part in parts:
                await ctx.send(f"```{part}```")
        except KeyError:
            await ctx.send("No lists available!")

    @commands.command(name="listview", aliases=["viewlist", "list"])
    @commands.cooldown(1, 3)
    async def list_view(self, ctx, *, list_name: str):
        """
        View a list.
        """
        try:
            list_name = list_name.lower()
            list_content = self.lists[str(ctx.author.id)][list_name]

            content = f"{ctx.author.name}'s List - {list_name.capitalize()}\n\n"
            i = 0
            for item in list_content:
                i += 1
                content += f"{i} - {item}\n"

            parts = [(content[i:i + 1500]) for i in range(0, len(content), 1500)]
            for part in parts:
                await ctx.send(f"```{part}```")
        except KeyError:
            await ctx.send("No lists available!")

    @commands.command(name="listitemadd", aliases=["additem"])
    @commands.cooldown(1, 3)
    async def list_item_add(self, ctx, list_name: str, *, item: str):
        """
        Add an item to a list.
        """
        list_name = list_name.lower()

        if not str(ctx.author.id) in self.lists:
            await ctx.send("No lists available!")
            return

        if list_name not in self.lists[str(ctx.author.id)]:
            await ctx.send("That list does not exist!")
            return

        current_content = self.lists[str(ctx.author.id)][list_name]
        current_content.append(item)

        self.lists[str(ctx.author.id)].update({list_name: current_content})
        lc.update_users(self.lists)
        lc.save_data()
        await ctx.send(f"Added `{item}` to list `{list_name}`.")

    @commands.command(name="listitemdelete", aliases=["delitem"])
    @commands.cooldown(1, 3)
    async def list_item_delete(self, ctx, list_name: str, item_num: int):
        """
        Remove an item from a list.
        """

        list_name = list_name.lower()

        if not str(ctx.author.id) in self.lists:
            await ctx.send("No lists available!")
            return

        if list_name not in self.lists[str(ctx.author.id)]:
            await ctx.send("That list does not exist!")
            return

        current_content = self.lists[str(ctx.author.id)][list_name]
        del current_content[item_num-1]

        self.lists[str(ctx.author.id)].update({list_name: current_content})
        lc.update_users(self.lists)
        lc.save_data()
        await ctx.send(f"Removed item from list `{list_name}`.")


def setup(bot):
    bot.add_cog(Lists(bot))
