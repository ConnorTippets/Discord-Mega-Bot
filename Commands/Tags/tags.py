import discord
from discord.ext import commands
import os
import tabulate
from jishaku.paginators import PaginatorEmbedInterface

class TagsInterface(PaginatorEmbedInterface):
    def __init__(self, *args, **kwargs):
        self.tags = kwargs.pop("tags", None)
        super().__init__(*args, **kwargs)
    
    @property
    def send_kwargs(self) -> dict:
        display_page = self.display_page
        self._embed.description = self.pages[display_page]
        self._embed.set_footer(text=f'Page {display_page + 1}/{self.page_count} | {len(self.tags)} {"entries" if not len(self.tags) == 1 else "entry"}')
        return {'embed': self._embed}

class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.group(brief='Tag system', invoke_without_command=True)
    async def tag(self, ctx, *, tag):
        cur = self.bot.db.execute('SELECT content FROM tags WHERE name = ?', (tag,))
        result = cur.fetchall()
        if result == []:
            return await ctx.send('Unknown tag')
        else:
            await ctx.send(result[0][0])
    
    @tag.command(brief='Creates a tag', aliases=['make'])
    async def create(self, ctx, name, *, content):
        if name in [c.name for c in ctx.command.root_parent.commands]:
            return await ctx.send('Name is a reserved word.')
        elif name in [c[0] for c in self.bot.db.execute('SELECT name FROM tags').fetchall()]:
            return await ctx.send('A tag with that name already exists.')
        else:
            self.bot.db.execute('INSERT INTO tags(name, author_id, content) VALUES (?, ?, ?)', (name, ctx.author.id, content,))
            self.bot._conn.commit()
            await ctx.send(f'Created tag with name `{name}` successfully.')
    
    @tag.command(brief='Deletes a tag, if you have the permission to do so', aliases=['remove'])
    async def delete(self, ctx, name):
        if not name in [c[0] for c in self.bot.db.execute('SELECT name FROM tags').fetchall()]:
            return await ctx.send('A tag with that name doesn\'t exist.')
        tag_author = self.bot.db.execute('SELECT author_id FROM tags WHERE name = ?', (name,)).fetchall()
        if not ctx.author.id == tag_author[0][0]:
            return await ctx.send('You do not own this tag.')
        else:
            self.bot.db.execute('DELETE FROM tags WHERE name = ?', (name,))
            self.bot._conn.commit()
            await ctx.send(f'Tag `{name}` successfully deleted.')
    
    @tag.command(brief='Edits a tag, if you have the permission to do so')
    async def edit(self, ctx, name, *, content):
        if not name in [c[0] for c in self.bot.db.execute('SELECT name FROM tags').fetchall()]:
            return await ctx.send('A tag with that name doesn\'t exist.')
        tag_author = self.bot.db.execute('SELECT author_id FROM tags WHERE name = ?', (name,)).fetchall()
        if not ctx.author.id == tag_author[0][0]:
            return await ctx.send('You do not own this tag.')
        else:
            self.bot.db.execute('UPDATE tags SET content = ? WHERE name = ?', (content, name,))
            self.bot._conn.commit()
            await ctx.send(f'Tag `{name}` successfully edited.')
    
    @tag.group(brief='Shows all tags', invoke_without_command=True)
    async def all(self, ctx):
        tags = self.bot.db.execute('SELECT name, id FROM tags').fetchall()
        paginator = commands.Paginator(max_size=1900, prefix='', suffix='')
        for id, tags in enumerate(tags):
            paginator.add_line(f'{id+1}. {tags[0]}')
        interface = TagsInterface(ctx.bot, paginator, owner=ctx.author, embed=discord.Embed(title='All Tags', color=0x2F3136), tags=tags)
        await interface.send_to(ctx)
    
    @all.command(brief='Shows all tags, in text form')
    async def text(self, ctx):
        cur = self.bot.db.execute('SELECT * FROM tags')
        tags = cur.fetchall()
        names = [description[0] for description in cur.description]
        table = tabulate.tabulate(tags, names, tablefmt='pretty')
        f = open("tags.txt", "w+")
        f.write(table)
        f.close()
        await ctx.send(file=discord.File("tags.txt"))
        os.remove("tags.txt")
    
    @tag.command(brief='Searches through the tags for your query')
    async def search(self, ctx, *, query):
        if not query.startswith("id "):
            names = [c[0] for c in self.bot.db.execute('SELECT name FROM tags').fetchall()]
            results = await self.bot.utils.find(query, names)
            if results == []:
                return await ctx.send('No tags found.')
            paginator = commands.Paginator(max_size=1900, prefix='', suffix='')
            for id, name in enumerate(results):
                tag_id = self.bot.db.execute('SELECT id FROM tags WHERE name = ?', (name,)).fetchall()[0][0]
                paginator.add_line(f'{id+1}. {name} (ID: {tag_id})')
            interface = TagsInterface(ctx.bot, paginator, owner=ctx.author, embed=discord.Embed(title='Tag Search', color=0x2F3136), tags=results)
            await interface.send_to(ctx)
        else:
            id = int(query.strip("id "))
            name = self.bot.db.execute('SELECT name FROM tags WHERE id = ?', (id,)).fetchall()
            if name == []:
                return await ctx.send(f'No tag with the id {id} found.')
            paginator = commands.Paginator(max_size=1900, prefix='', suffix='')
            paginator.add_line(f'1. {name[0][0]} (ID: {id})')
            interface = TagsInterface(ctx.bot, paginator, owner=ctx.author, embed=discord.Embed(title='Tag Search', color=0x2F3136), tags=name)
            await interface.send_to(ctx)
    
    @commands.command(brief='Shows the tags of the person specified')
    async def tags(self, ctx, member:discord.Member=None):
        member = member or ctx.author
        tags = self.bot.db.execute('SELECT name, id FROM tags WHERE author_id = ?', (member.id,)).fetchall()
        if tags == []:
            return await ctx.send('You have no tags.')
        paginator = commands.Paginator(max_size=1900, prefix='', suffix='')
        for id, tag in enumerate(tags):
            paginator.add_line(f'{id+1}. {tag[0]} (ID: {tag[1]})')
        interface = TagsInterface(ctx.bot, paginator, owner=ctx.author, embed=discord.Embed(color=0x2F3136).set_author(name='Tags', icon_url=member.avatar), tags=tags)
        await interface.send_to(ctx)
 
async def async_setup(bot):
  await bot.add_cog(Tags(bot))

def setup(bot):
  return async_setup(bot)
  bot.add_cog(Tags(bot))
