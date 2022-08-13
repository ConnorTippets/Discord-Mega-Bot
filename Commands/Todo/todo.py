import discord
from discord.ext import commands
from discord.ext import flags
from jishaku.paginators import WrappedPaginator, PaginatorEmbedInterface

class Todo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.group(aliases=['to-do'])
    async def todo(self, ctx):
        pass
    
    @todo.command()
    async def list(self, ctx, member:discord.Member=None):
        member = member or ctx.author
        result = self.bot.db.execute('SELECT * FROM todos WHERE user_id = ?', (member.id,)).fetchall()
        if result == []:
            return await ctx.send('You have no todo items!')
        embed = discord.Embed(title='Todo List', color=0x2F3136)
        paginator = WrappedPaginator(max_size=1900)
        for i in range(len(result)):
            paginator.add_line(f'[{i+1}] {result[i][1]}'.replace("`", "\u200b`"))
        interface = PaginatorEmbedInterface(ctx.bot, paginator, owner=ctx.author, embed=embed)
        await interface.send_to(ctx)
    
    @todo.command()
    async def add(self, ctx, *, entry:str):
        if self.bot.db.execute('SELECT * FROM todos WHERE user_id = ? AND entry_name = ?', (ctx.author.id, entry,)).fetchall() == []:
            self.bot.db.execute('INSERT INTO todos(user_id, entry_name) VALUES (?, ?)', (ctx.author.id, entry,))
            self.bot._conn.commit()
            return await ctx.send('Added to your todo list!')
        await ctx.send('That item already exists.')
    
    @todo.command()
    async def remove(self, ctx, *, entry_id:int):
        all = self.bot.db.execute('SELECT * FROM todos WHERE user_id = ?', (ctx.author.id,)).fetchall()
        for i in range(len(all)):
            if entry_id == i+1:
                self.bot.db.execute('DELETE FROM todos WHERE user_id = ? AND entry_name = ?', (ctx.author.id, all[i][1]))
                self.bot._conn.commit()
                return await ctx.send('Removed from your todo list!')
        await ctx.send('That item doesn\'t exist.')

async def async_setup(bot):
  await bot.add_cog(Todo(bot))

def setup(bot):
  return async_setup(bot)
  bot.add_cog(Todo(bot))
