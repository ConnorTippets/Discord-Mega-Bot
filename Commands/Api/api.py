import discord
from discord.ext import commands, menus
import json
from Utils.utils import Utils, RawMessage
import unicodedata
from bottom import to_bottom, from_bottom
import base64
import random
import humanize
import datetime
import time
import asyncio
import udpy
from discord.ext.commands.cooldowns import BucketType
from jishaku.paginators import WrappedPaginator, PaginatorEmbedInterface
import string

class EmbedUrbanSource(menus.ListPageSource):
    async def format_page(self, menu, item):
        embed = discord.Embed(title=item.word, description=item.definition if not len(item.definition) > 2048 else item.definition[:(2048-15)] + '[More chars...]')
        return embed

class EmbedMSGSource(menus.ListPageSource):
    async def format_page(self, menu, item):
        embed = discord.Embed(description=item.jump_url).set_author(name=item.author.name, icon_url=item.author.avatar_url)
        return embed

def to_string(c):
    digit = f'{ord(c):x}'
    name = unicodedata.name(c, 'Can not find')
    return f'`\\U{digit:>08}`= {name}'

squares = ['⬛', '⬜', '🟫', '🟥', '🟦', '🟩', '🟨', '🟧']
rule = {str(i): squares[i] for i in range(8)}
rulen = {f"{chr(o+ord('A'))}": o+10 for o in range(26)} | {f"{chr(o+ord('a'))}": o+36 for o in range(26)}
rulena = {o+10 : f"{chr(o+ord('A'))}" for o in range(26)} | {o+36 : f"{chr(o+ord('a'))}" for o in range(26)}
def toEmoji(e):
    for k in rule.keys():
        e = e.replace(k, rule[k])
    for x in string.printable.replace(' ', '').replace('\n', ''):
        e = e.replace(x, "")
    return e

def fromEmoji(e):
    for k in rule.keys():
        e = e.replace(rule[k], k)
    return e

def toNum(e):
    for k in rulen.keys():
        e = e.replace(k, str(rulen[k]))
    return e

#def fromNum(e):
#    x = 0
#    while x < len(e):
#        e = e.replace(e[x] + e[x+1], rulena[int(e[x] + e[x+1])])
#        x+=2
#    return e

class API(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.utils = Utils(self.bot)
        self.urban = udpy.UrbanClient()
    
    async def do_rtfs(self, query, library):
        async with self.bot.session.get('https://idevision.net/api/public/rtfs', params={'query': query, 'library': library}) as resp:
            if not resp.status == 400:
                response = await resp.json()
                nodes = response['nodes']
                time = response['query_time']
            else:
                nodes, time = None
        return nodes, time
    
    async def do_rtfm(self, query, library):
        if library in ('discord.py', 'd.py', 'dpy'):
            library = "https://discordpy.readthedocs.io/en/stable"
        elif library in ('python', 'py'):
            library = "https://docs.python.org/3/"
        async with self.bot.session.get('https://idevision.net/api/public/rtfm', params={'query': query, 'location': library}) as resp:
            if not resp.status == 400:
                response = await resp.json()
                nodes = response['nodes']
                time = response['query_time']
            else:
                nodes, time = None
        return nodes, time
    
    @commands.command(brief='Shows the raw data of a message')
    async def msgraw(self, ctx, id):
        await ctx.send(self.utils.codeblock(json.dumps(await self.bot.http.get_message(ctx.channel.id, id), indent=4), language='json'))
    
    @commands.command(brief='Shows the raw data of a user')
    async def userraw(self, ctx, id):
        await ctx.send(self.utils.codeblock(json.dumps(await self.bot.http.get_user(id), indent=4), language='json'))
    
    @commands.command(brief='Shows the raw data of a server')
    async def guildraw(self, ctx, id):
        try:
            await ctx.send(self.utils.codeblock(json.dumps(await self.bot.http.get_guild(id), indent=4), language='json'))
        except discord.HTTPException:
            await ctx.send('Output too long, but the code for uploading to mystbin is curretly broken.')
    
    @commands.command(brief='Shows unicode info on a character')
    async def charinfo(self, ctx, *, char:str):
        values = []
        for value in char:
            values.append(to_string(value))
        await ctx.send('\n'.join(values))
    
    @commands.command(brief='Maps numbers to emojis')
    async def grid(self, ctx, *, content:commands.clean_content):
        x = toEmoji(content)
        x = await ctx.send(x.strip("")) if x else None
    
    @commands.group(brief='Encodes and decodes bottom')
    async def bottom(self, ctx):
        pass
    
    @bottom.command(brief='Encodes into bottom')
    async def encode(self, ctx, *, content:str):
        await ctx.send('```\n' + to_bottom(content) + '\n```')
    
    @bottom.command(brief='Decodes out of bottom')
    async def decode(self, ctx, *, content:str):
        await ctx.send('```\n' + from_bottom(content) + '\n```')
    
    @commands.command(aliases=['pt'], brief='Shows the id belonging to the token')
    async def parsetoken(self, ctx, token:str):
        id = base64.b64decode(token.split('.')[0])
        await ctx.send(f'The id belonging to this token is {id.decode()}')
    
    @commands.command(aliases=['rm'], brief='Shows a random message from the current channel')
    async def randommessage(self, ctx, limit:int=100):
        start = time.perf_counter()
        messages = await ctx.channel.history(limit=limit).flatten()
        messages.reverse()
        message = random.choice(messages)
        end = time.perf_counter()
        e = discord.Embed(description=message.content, color=0x2F3136)
        e.set_footer(text='ID: '+str(message.id) + ', Took ' + str(round((end - start)*1000, 6)) + 'ms to find message')
        e.add_field(name='jump url', value=f'[jump!]({message.jump_url})')
        e.set_author(icon_url=message.author.avatar.url, name=message.author.name)
        await ctx.send(embed=e)
    
    @commands.command(aliases=['rma'], brief='Shows a random message sent by you in the current channel')
    async def randmessageauth(self, ctx, limit:int=100):
        start = time.perf_counter()
        messages = [message for message in (await ctx.channel.history(limit=limit).flatten()) if message.author.name == ctx.author.name]
        message = random.choice(messages)
        end = time.perf_counter()
        e = discord.Embed(description=message.content, color=0x2F3136)
        e.set_footer(text='ID: '+str(message.id) + ', Took ' + str(round((end - start)*1000, 6)) + 'ms to find message')
        e.add_field(name='jump url', value=f'[jump!]({message.jump_url})')
        e.set_author(icon_url=message.author.avatar.url, name=message.author.name)
        await ctx.send(embed=e)
    
    @commands.command(aliases=['e'], brief='Sends an embed')
    async def embed(self, ctx, *options):
        await ctx.send(embed=discord.Embed.from_dict(json.loads("".join(options).replace("'", "\""))))
    
    @commands.command(aliases=['re'], brief='Shows your edit history')
    async def recent_edits(self, ctx):
        formats = []
        messages = {}
        for id in self.bot.edit_history:
            if self.bot.edit_history[id].author.id == ctx.author.id:
                messages[id] = self.bot.edit_history[id]
        
        for k, v in messages.items():
            formats.append(f'Message {list(messages).index(k)+1}:')
            m = v
            formats.append(f'   No. 1 at {m.created_at}: {m.content}')
            formats.append('\n')
        
        embed = discord.Embed(title='Recent Edits', description='\n'.join(formats), color=0x2F3136)
        await ctx.send(embed=embed)
    
    @commands.command(brief='Shows you the urban definition of a word')
    async def urban(self, ctx, *, word:str):
        entries = self.urban.get_definition(word)
        if entries == []:
            return await ctx.send(embed=discord.Embed(title="No results found", description=f"No entries were found for query '{word}'"))
        menu = menus.MenuPages(EmbedUrbanSource(entries, per_page=1))
        await menu.start(ctx)
    
    @commands.command(brief='Looks up a message in the channel specified')
    async def msglookup(self, ctx, channel:discord.TextChannel, *, content:str):
        entries = await self.utils.find(content, await channel.history().flatten(), key=lambda m: m.content)
        if entries == []:
            return await ctx.send(embed=discord.Embed(title="No results found", description=f"No entries were found for query '{content}'"))
        menu = menus.MenuPages(EmbedMSGSource(entries, per_page=1))
        await menu.start(ctx)
    
    @commands.command(brief='Reports a bug to the dev team')
    async def reportbug(self, ctx, bug):
        await ctx.send('Bug reported.')
        self.bot.dispatch('bug', ctx, ctx.author, bug)
    
    @commands.Cog.listener()
    async def on_bug(self, ctx, author, bug):
        self.bot.db.execute('INSERT INTO bugs(author, bug) VALUES (?, ?)', (author.id,bug))
        channel = self.bot.get_channel(826610452653146152)
        emb = discord.Embed(description=bug).set_author(name='Bug Report', icon_url=author.avatar_url)
        await channel.send(embed=emb)
        await self.bot.get_user(376129806313455616).send(embed=emb)
    
    @commands.command(brief='Searches for the source of modules')
    @commands.cooldown(1,5,BucketType.user)
    async def rtfs(self, ctx, library = 'discord.py', *, query):
        library = library if not library == 'dpy' else 'discord.py'
        nodes, time = await self.do_rtfs(query, library)
        if nodes == {}:
            return await ctx.send('No results found.')
        if nodes is None and time is None:
            return await ctx.send('Library is not available.')
        emb = discord.Embed(title=f'Results for "{query}" in {library}', description='\n'.join([f'[{node_name}]({node_source})' for node_name, node_source in nodes.items()]), color=0x2F3136)
        emb.set_footer(text=f'Query Time: {round(time * 1000, 6)}ms')
        await ctx.send(embed=emb)
    
#    @commands.command(brief='Encodes the alphabet into a decimal format.')
#    async def encode(self, ctx, *, content):
#        await ctx.send(toNum(content))
#    
#    @commands.command(brief='Decodes decimal format into the alphabet.')
#    async def decode(self, ctx, *, content):
#        await ctx.send(fromNum(content))
    
    @commands.command(brief='Searches for the documentation of modules')
    @commands.cooldown(1,5,BucketType.user)
    async def rtfm(self, ctx, library = 'discord.py', *, query):
        nodes, time = await self.do_rtfm(query, library)
        if nodes == {}:
            return await ctx.send('No results found.')
        if nodes is None and time is None:
            return await ctx.send('Library is not available.')
        emb = discord.Embed(title=f'Results for "{query}" in {library}', description='\n'.join([f'[{node_name}]({node_source})' for node_name, node_source in nodes.items()]), color=0x2F3136)
        emb.set_footer(text=f'Query Time: {round(float(time) * 1000, 6)}ms')
        await ctx.send(embed=emb)

async def async_setup(bot):
  await bot.add_cog(API(bot))

def setup(bot):
  return async_setup(bot)
  bot.add_cog(API(bot))
