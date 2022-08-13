import discord
from discord.ext import commands, ipc
from properties import dagpi_token, google_key, ipc_key, genius_key
from asyncdagpi import Client
import lyricsgenius
import mystbin
import time
import json
import asyncio
import os
import humanize
import datetime as dt
import async_cse as cse
from aiohttp import ClientSession
from eight_ball import Ball
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from sqlite3 import connect as conn
from fakefiles import FakeFiles
import inspect
import logging
from conlan import ConLan
import re
from pathlib import Path
import io

messaging_logger = logging.getLogger("Commands")
messaging_logger.setLevel(logging.DEBUG)
messaging_logger_file_handler = logging.FileHandler('bot.log', 'w')
messaging_logger_file_handler.setLevel(logging.DEBUG)
messaging_logger_file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s'))
messaging_logger.addHandler(messaging_logger_file_handler)

class Utils:
    def __init__(self, bot):
        self.bot = bot
    
    async def to_url(self, ctx, x):
        _ = discord.utils.get(self.bot.users, name=x)
        if not _:
            if not x:
                try:
                    x = ctx.message.attachments[0].url
                except:
                    x = ctx.author.avatar.url
        else:
            x = _.avatar.url
        try:
            async with self.bot.session.get(x) as r:
                r = await r.read()
        except:
            raise ctx.CommandError('Cannot convert argument into url.')
        return x
    
    def strl(self, a:list):
        h = ""
        for g in a:
            h+=g
        return h
    def addChar(self, char:str, adder:list, referencer:list):
        for x in range(len(referencer)):
            if referencer[x] == char:
                adder[x] = (char + adder[x])
        return adder
    def strd(self, a:list):
        h = ""
        for g in a:
            h+=(str(g)+'\n')
        return h
    def bot_mentioned_in(self, message:discord.Message):
        if message.content == f'<@{message.guild.me.id}>':
            return True
        else:
            return False
    def indent(self, code:str):
        code = code.split('\n')
        for line_index in range(len(code)):
          if code[line_index].endswith(':') and not code[line_index+1].startswith(" "):
            code[line_index+1] = '    ' + code[line_index+1]
        return '\n'.join(code)
    def codeblock(self, code:str, *, language:str='python', no_single_line:bool=True):
        if len(code.split('\n')) == 1 and no_single_line:
            code = f'`{code}`'
            return code
        code = f'```{language}\n{code}\n```'
        return code
    
    def prefix_for(self, bot, guild:discord.Guild):
        return bot.prefixes[str(guild.id)]
    
    async def moving_bar(self, *, length:int=20):
        states = []
        states.append('`[' + ' '*(length+1) + ']`')
        for i in range(1, length+1):
            states.append(f'`{"[" + "#"*i + " "*(length-i) + "]"}`')
        return states
    
    async def sembed(self, ctx, *, title=None, description=None, color=None, author_url=None, author_name=None, footer_text=None, fields=None, image_url=None, thumbnail_url=None):
        embed=discord.Embed(title=title, description=description, color=color)
        if author_url and author_name:
            embed.set_author(icon_url=author_url, name=author_name)
        if footer_text:
            embed.set_footer(text=footer_text)
        if fields:
            for field_name, field_value in fields.items():
                embed.add_field(name=field_name, value=field_value)
        if image_url:
            embed.set_image(url=image_url)
        if thumbnail_url:
            embed.set_thumbnail(url=thumbnail_url)
        await ctx.send(embed=embed)
    
    async def screenshot_web(self, url:str):
        options = Options()
        options.headless = True
        #options = webdriver.ChromeOptions()
        #options.headless = True
        #driver = webdriver.Chrome(r"C:\Users\Meisc\Downloads\chromedriver_win32\chromedriver.exe", options=options)
        driver = webdriver.Firefox(executable_path='C:\Program Files\geckodriver.exe', options=options)
        driver.get(url)
        await asyncio.sleep(1)
        
        #driver.get_screenshot_as_file("screenshot.png")
        sc = driver.get_screenshot_as_png()
        driver.quit()
        return discord.File(io.BytesIO(sc), 'screen.png')
        #return discord.File("screenshot.png")
    
    async def imaging_api(self, route:str, **kwargs):
        imaging = (self.bot.get_command('control_point')).cog
        _ = getattr(imaging, route)
        if _:
            return await _(**kwargs)
        else:
            return io.BytesIO()
    
    async def compute_code(self, code:str):
        interp = ConLan(self.bot)
        output = await interp.run(code)
        return output
    
    async def detect_self_bots(self, ctx):
        for channel in ctx.text_channels:
            async for message in channel.history():
                 try:
                     banned_users = await ctx.bans()
                     for ban_entry in banned_users:
                         user = ban_entry.banned_users
                         
                         if str(user) == str(message.author) and str(message.embeds) != '[]' and not user.bot:
                             self.bot.self_bots[message.guild.id][str(message.author)] = 'self-bot'
                 except:
                     if str(message.embeds) != '[]' and not message.author.bot:
                         self.bot.self_bots[message.guild.id][str(message.author)] = 'self-bot'
    
    async def sql_to_json(self, list, *, indent=4):
        thingy = [f'{" "*indent}"{i[0]}": "{i[1]}",' for i in list]
        thingy[-1] = thingy[-1].removesuffix(',')
        return '{\n' + '\n'.join(thingy) + '\n}'
    
    async def source(self, func: callable, *, codeblock=False):
        return (inspect.getsource(func) if not type(func) in [commands.Command, commands.Group] else inspect.getsource(func.callback)) if not codeblock else (f'```py\n{inspect.getsource(func)}\n```' if not type(func) in [commands.Command, commands.Group] else f'```py\n{inspect.getsource(func.callback)}\n```')
    
    async def find(self, query, seq, *, key = lambda x: x):
        results = []
        for elem in seq:
            try:
                if key(elem) == query or key(elem).startswith(query) or key(elem).endswith(query):
                    results.append(elem)
            except AttributeError:
                if key(elem) == query:
                    results.append(elem)
        return results
    
    async def humanize_list(self, lst):
        items = len(lst)
        if items == 0:
            return ''
        elif items == 1:
            return lst[0]
        else:
            return ', '.join(lst[:-1]) + f' and {lst[-1]}'
    
    async def regex(self, match, subject):
        matches = re.findall(r"{}".format(match), subject)
        if not matches:
            return 'Found no matches.'
        else:
            return f'Found `{len(matches)}` {"matches" if len(matches) != 1 else "match"}: `{await self.humanize_list(matches)}`'

class DMBText(commands.Context):
    def __lshift__(self, arg):
        return self.send(arg)
    
    @property
    def is_subclassed(self):
        return not type(self) == commands.Context
    
    async def tick(self, value):
        emoji = '\N{WHITE HEAVY CHECK MARK}' if value else '\N{CROSS MARK}'
        await self.message.add_reaction(emoji)
    
    async def sembed(self, *, title=None, description=None, color=None, author_url=None, author_name=None, footer_text=None, fields=None, image_url=None, thumbnail_url=None):
        embed=discord.Embed(title=title, description=description, color=color)
        if author_url and author_name:
            embed.set_author(icon_url=author_url, name=author_name)
        if footer_text:
            embed.set_footer(text=footer_text)
        if fields:
            for field_name, field_value in fields:
                embed.add_field(name=field_name, value=field_value)
        if image_url:
            embed.set_image(url=image_url)
        if thumbnail_url:
            embed.set_thumbnail(url=thumbnail_url)
        await self.send(embed=embed)
    
    async def paste(self, data, *, syntax='python'):
        await self.send(await self.bot.mystbin.post(data, syntax=syntax))
    
    async def send(self, content=None, **kwargs):
        if str(self.author.id) in json.load(open('./bans.json', 'r')):
            msg = await super().send('You are blacklisted from this bot.')
            return msg
        msg = await super().send(content, **kwargs)
        return msg
    
    async def owoify(self, text:str):
        return text.replace('l', 'w').replace('L', 'W').replace('r', 'w').replace('R', 'W').replace('o', 'owo').replace('O', 'OWO')

    class CommandError(Exception):
        pass

class BoolConverter(commands.Converter):
        async def convert(self, ctx, argument):
            if argument.lower() in ('yes', 'correct', 'agree', '1', 'right', 'true'):
                return True
            elif argument.lower() in ('no', 'incorrect', 'disagree', '0', 'wrong', 'false'):
                return False
            else:
                return False

def construct_cogs():
    bp = os.getcwd()
    os.chdir(bp + "/Commands/")
    path = Path('.')
    subdirs = []
    for x in path.iterdir():
        if x.is_dir() and not str(x) == "__pycache__":
            subdirs.append(x)
    cogs = []
    cogsidx = 0
    for dis in subdirs:
        cogs.append([])
        cogs[cogsidx].append(str(dis))
        constructed_path = f'Commands.{cogs[cogsidx][0]}.{cogs[cogsidx][0].lower()}'
        cogs[cogsidx] = constructed_path
        cogsidx = cogsidx + 1
    os.chdir(bp)
    return cogs

class DMBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.remove_command('help')
        self._commands = 0
        self.currency_cache = {}
        self.dag = Client(dagpi_token)
        self.mystbin = mystbin.Client()
        self._start = time.time()
        self._prefixes = json.load(open('./prefixes.json', 'r'))
        self._banned = json.load(open('./bans.json', 'r'))
        self._edit_cache = {}
        self.cse = cse.Search(google_key)
        self.ipc = ipc.Server(self, secret_key=ipc_key)
        self.genius = lyricsgenius.Genius(genius_key)
        self.genius.verbose = False
        self.ball = Ball()
        self.self_bots = {}
        self.utils = Utils(self)
        self._conn = conn('exampledb.db')
        self.db = self._conn.cursor()
        self.description = 'A big bot, with lots of features.'
        self.prefixless = False
        self.words_said = {}
        self.edit_history = {}
        self.events_dispatched = {}
        self.log = messaging_logger
        self.get_message = self._connection._get_message
        self.fakefiles = FakeFiles(self)
        self.cog_paths = construct_cogs()
        asyncio.run(self.load_extension('jishaku'))
        os.environ["JISHAKU_NO_UNDERSCORE"] = "true"
        os.environ["JISHAKU_NO_DM_TRACEBACK"] = "true" 
        os.environ["JISHAKU_HIDE"] = "true"
        asyncio.run(self.reload_extension('jishaku'))
        for path in self.cog_paths:
            asyncio.run(self.load_extension(path))
    
    async def on_ipc_ready(self):
        """Called upon the IPC Server being ready"""
        print("Ipc is ready.")
    
    async def on_ipc_error(self, endpoint, error):
        """Called upon an error being raised within an IPC route"""
        print(endpoint, "raised", error)
    
    @property
    def commands_re(self):
        return self._commands
    
    @property
    def commands_dc(self):
        return {f'{f"{cmd.root_parent.name} " if cmd.root_parent else ""}{cmd.name}' : cmd for cmd in self.walk_commands()}
    
    @property
    def uptime(self):
        return humanize.naturaldelta(dt.timedelta(seconds=time.time() - self._start))
    
    @property
    def prefixes(self):
        return self.db.execute('SELECT * FROM prefixes').fetchall()
    
    @property
    def bans(self):
        return json.load(open('./bans.json', 'r'))
    
    def guild_cfg(self, guild:discord.Guild):
        return {'name': guild.name, 'prefix': self.prefix_for(guild), 'id': guild.id, 'user_count': guild.member_count, 'users': [str(m) for m in guild.members], 'humans': [str(m) for m in guild.members if not m.bot], 'bots': [str(m) for m in guild.members if m.bot]}
    
    def prefix_for(self, guild:discord.Guild):
        for row in self.prefixes:
            if row[0] == guild.id:
                return row[1]
        return '::'
    
    async def get_context(self, message, cls=DMBText):
        return await super(self.__class__, self).get_context(message, cls=cls)
    
    def dispatch(self, event_name, *args, **kwargs):
        super().dispatch(event_name, *args, **kwargs)
        super().dispatch('event', event_name)
    
    async def getPlayer(self, name):
        return await (await self.session.get(f'https://api.hypixel.net/player?key={hypixel_keys[0]}&name={name}')).json()

class RawMessage(discord.Message):
    def __init__(self, bot, channel_id, message_id):
        self._state = bot._connection
        self.id = message_id
        self.channel = bot.get_channel(channel_id) or discord.Object(channel_id)
    def __repr__(self):
        return 'lazy'

class CommandConverter(commands.Converter):
    async def convert(self, ctx, argument):
        bot = ctx.bot
        command = bot.get_command(argument)
        if command:
            return command
        else:
            isLower = True if bot.get_command(argument.lower()) else False
            isUpper = True if bot.get_command(argument.upper()) else False

            result = None
            if isLower:
                result = bot.get_command(argument.lower())
            elif isUpper:
                result = bot.get_command(argument.upper())
            
            if result:
                return result
            else:
                raise commands.CommandNotFound('Failed conversion of "{}" to Command'.format(argument))
