import discord
from discord.ext import commands
from discord.ext import ui
import sqlite3
import os
import subprocess as sp
from jishaku.codeblocks import codeblock_converter
import json
import random
from Commands.Games import games
import inspect
import asyncio
from Utils.utils import Utils
import time
from discord.ext import menus
from sqlite3 import connect
import typing
from jishaku.paginators import PaginatorEmbedInterface, PaginatorInterface, WrappedPaginator
import traceback
import import_expression
import tabulate
import io
import contextlib
import sys
from pytio import Tio, TioRequest

base_coro = """
async def func(env):
  import asyncio, discord, time
  from importlib import import_module as {0}
  from discord.ext import commands
  from discord.utils import find, get
  s = time.perf_counter()
  
""".format(import_expression.constants.IMPORTER)

class RegexFlags(commands.FlagConverter, prefix='--', delimiter='='):
    match: str
    subject: str

class InstantCMDSException(Exception):
    pass

class CommandObjects:
    def __init__(self, bot):
        self.bot = bot
        for command in bot.commands:
            setattr(self, command.name, command)
    
    async def all(self):
        return self.bot.commands_dc

class PaginatorTest(menus.Menu):
    async def send_initial_message(self, ctx, channel):
        self.places = ctx.choices
        self.place = 0
        return await channel.send(f'{self.places[self.place]}\n\nPage {self.place+1}/{len(self.places)}') if type(self.places[self.place]) != discord.Embed else await channel.send(f'{self.places[self.place]}\n\nPage {self.place+1}/{len(self.places)}', embed=self.places[self.place])
    
    @menus.button('\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}')
    async def on_empty_list(self, payload):
        self.place = 0
        if type(self.places[self.place]) == discord.Embed:
            return await self.message.edit(content='Page {self.place+1}/{len(self.places)}\n', embed=self.places[self.place])
        await self.message.edit(content=f'{self.places[self.place]}\n\nPage {self.place+1}/{len(self.places)}')
    
    @menus.button('\N{LEFTWARDS BLACK ARROW}')
    async def on_left_arrow(self, payload):
        if self.place == 0:
            return
        self.place -= 1
        if type(self.places[self.place]) == discord.Embed:
            return await self.message.edit(content='Page {self.place+1}/{len(self.places)}\n', embed=self.places[self.place])
        await self.message.edit(content=f'{self.places[self.place]}\n\nPage {self.place+1}/{len(self.places)}')
    
    @menus.button('\N{BLACK RIGHTWARDS ARROW}')
    async def on_right_arrow(self, payload):
        if self.place == len(self.places)-1:
            return
        self.place += 1
        if type(self.places[self.place]) == discord.Embed:
            return await self.message.edit(content='Page {self.place+1}/{len(self.places)}\n', embed=self.places[self.place])
        await self.message.edit(content=f'{self.places[self.place]}\n\nPage {self.place+1}/{len(self.places)}')
    
    @menus.button('\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}')
    async def on_full_list(self, payload):
        self.place = (len(self.places) - 1)
        if type(self.places[self.place]) == discord.Embed:
            return await self.message.edit(content='Page {self.place+1}/{len(self.places)}\n', embed=self.places[self.place])
        await self.message.edit(content=f'{self.places[self.place]}\n\nPage {self.place+1}/{len(self.places)}')
    
    @menus.button('\N{INPUT SYMBOL FOR NUMBERS}')
    async def on_random_page(self, payload):
        self.place = random.randint(0, len(self.places) - 1)
        if type(self.places[self.place]) == discord.Embed:
            return await self.message.edit(content='Page {self.place+1}/{len(self.places)}\n', embed=self.places[self.place])
        await self.message.edit(content=f'{self.places[self.place]}\n\nPage {self.place+1}/{len(self.places)}')
    
    @menus.button('\N{BLACK SQUARE FOR STOP}\ufe0f')
    async def on_stop(self, payload):
        self.stop()

currency_db_path = './Commands/Currency/currency.json'
class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.utils = Utils(self.bot)
        self._last_result = None
        self.cmd_env = {
            'discord': discord,
            'commands': commands,
            'asyncio': asyncio,
            'bot': None
        }
    
    async def attempt_tick(self, boolean, ctx):
        try:
            await ctx.tick(boolean)
        except (discord.NotFound, discord.HTTPException):
            return
    
    async def check_output(self, obj, ctx):
        if isinstance(obj, discord.Embed):
            await ctx.send(embed=obj)
        elif isinstance(obj, discord.File):
            await ctx.send(file=obj)
        elif isinstance(obj, type(None)):
            return
        elif isinstance(obj, list):
            if obj[-1] == "from_yield":
                for x in obj[:-1]:
                    await self.check_output(x, ctx)
            else:
                await ctx.send(obj)
        elif len([a for a in str(obj)]) > 2000:
            paginator = WrappedPaginator(max_size=1900, prefix='', suffix='')
            for line in str(obj).split('\n'):
                paginator.add_line(line)
            interface = PaginatorInterface(ctx.bot, paginator, owner=ctx.author)
            await interface.send_to(ctx)
        else:
            return await ctx.send(obj) if not obj in (None, '', discord.Embed, discord.File) else None
    
    async def async_execute(self, code, last_result, env):
        s = time.perf_counter()
        code = codeblock_converter(code)[1]
        env.update(globals())
        code = f'{base_coro}\n  ' + '\n  '.join(code.split('\n'))
        local = {}
        import_expression.exec(import_expression.compile(code, filename=env.get('filename', '<repl>'), mode='exec'), env, local)
        try:
            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                func = local['func']
                if inspect.isasyncgenfunction(func):
                    obj = [x async for x in func(env)] + ['from_yield']
                else:
                    obj = await func(env)
            obj = f.getvalue() if not f.getvalue() == '' else obj
            if not type(obj).__name__ == "list":
                self._last_result = obj
            else:
                if not obj[-1] == "from_yield":
                    self._last_result = obj
                else:
                    self._last_result = obj[-2]
        except Exception as e:
            await self.attempt_tick(False, env['ctx'])
            try:
                etype = type(e)
                trace = e.__traceback__
                return '```py\n' + ''.join(traceback.format_exception(etype, e, trace)).replace('C:\\Users\\Meisc\\Desktop\\Documents\\Discord Bot\\The Former\\Discord Mega Bot', '[HOME PATH]').replace('C:\\Users\\Meisc\\AppData\\Local\\Programs\\Python', '[PYTHON PATH]') + '\n```'
            except:
                return f'```py\n{str(e)}\n```'
        await self.attempt_tick(True, env['ctx'])
        await self.check_output(obj, env['ctx'])
    
    @commands.group()
    @commands.is_owner()
    async def dev(self, ctx):
        pass
    
    @dev.command()
    async def eval(self, ctx, *, code:str):
        cog = self.bot.get_cog("Jishaku")
        res = codeblock_converter(code)
        await cog.jsk_python(ctx, argument=res)
    
    @dev.command()
    async def status(self, ctx, *, activity):
        activity = discord.Game(activity)
        await self.bot.change_presence(status=discord.Status.online, activity=activity)
        await ctx.send(f'Changed activity to {activity}.')
    
    @dev.command()
    async def stop(self, ctx):
        emoji = '\N{THUMBS UP SIGN}'
        message = ctx.message
        await message.add_reaction(emoji)
        await ctx.bot.close()
    
    @dev.command()
    async def give(self, ctx, member:discord.Member, money:int):
        with open(currency_db_path, 'r') as f:
            currency = json.load(f)
        
        currency[str(member.id)] += money
        self.bot.currency_cache = currency
        
        with open(currency_db_path, 'w') as f:
            json.dump(currency, f, indent=4)
        await ctx.send('Given {} {} dollars(s)'.format(member.name, money))
    
    @dev.command()
    async def take(self, ctx, member:discord.Member, money:int):
        with open(currency_db_path, 'r') as f:
            currency = json.load(f)
        
        currency[str(member.id)] -= money
        self.bot.currency_cache = currency
        
        with open(currency_db_path, 'w') as f:
            json.dump(currency, f, indent=4)
        await ctx.send('Taken {} dollar(s) from {}'.format(money, member.name))
    
    @dev.command()
    async def set(self, ctx, member:discord.Member, money:int):
        with open(currency_db_path, 'r') as f:
            currency = json.load(f)
        
        currency[str(member.id)] = money
        self.bot.currency_cache = currency
        
        with open(currency_db_path, 'w') as f:
            json.dump(currency, f, indent=4)
        await ctx.send('Set {}\'s amount of dollar(s) to be {}'.format(member.name, money))
    
    @dev.command()
    async def remove(self, ctx, member:discord.Member):
        with open(currency_db_path, 'r') as f:
            currency = json.load(f)
        
        del currency[str(member.id)]
        self.bot.currency_cache = currency
        
        with open(currency_db_path, 'w') as f:
            json.dump(currency, f, indent=4)
        await ctx.send('Removed {} from database'.format(member.name))
    
    @dev.command(name='help')
    async def devHelp(self, ctx):
        await ctx.author.send(embed = discord.Embed(title="Developer Commands", color=0x2F3136, description='\n'.join([c.name for c in self.bot.get_cog('Admin').__cog_commands__])))
    
    @dev.command()
    async def eval_python(self, ctx, *, code:str):
        f = open('Evaluation/code.py', 'w')
        code = self.bot.utils.indent(code)
        code = code.replace('```py\n', '')
        code = code.replace('```python\n', '')
        code = code.replace('\n```', '')
        code = code.replace('```', '')
        f.write(code)
        f.close()
        code = code.split('\n')
        for line_index in range(len(code)):
            code[line_index] = '>>> ' + code[line_index]
        await ctx.tick(not sp.getoutput('py Evaluation/code.py').startswith('Traceback (most recent call last):'))
        if sp.getoutput('py Evaluation/code.py') == '':
            embed = discord.Embed(title="An Exception Occurred", description = '```py\n' + 'Traceback (most recent call last):\n    File "Evaluation/code.py", line {} in <module>\n        {}\nNoResponse: No response returned, you most likely forget to print your result'.format(len(code), code[len(code)-1].strip('>>> ')) + '\n```', color=0x2F3136)
            await ctx.send(embed=embed)
            return
        elif sp.getoutput('py Evaluation/code.py').startswith('Traceback (most recent call last):'):
            embed = discord.Embed(title="An Exception Occurred", description = '```py\n' + sp.getoutput('py Evaluation/code.py') + '\n```', color=0x2F3136)
            await ctx.send(embed=embed)
            return
        embed = discord.Embed(title="Evaluation", color=0x2F3136, description='```py\n' + ('\n'.join(code)) + '\n' + sp.getoutput('py Evaluation/code.py').replace(self.bot.http.token, '{token redacted}') + '\n```')
        await ctx.send(embed=embed)
    
    @dev.command()
    async def remmessages(self, ctx):
        async for message in ctx.channel.history():
            try:
                await message.delete()
            except discord.Forbidden:
                continue
        await ctx.send('Removed all my messages from 2 weeks ago onwards')
    
    @dev.command()
    async def testingServer(self, ctx):
        await ctx.send('https://discord.gg/H9Zd9ZYE6T')
    
    @dev.command()
    async def support(self, ctx):
        await ctx.send('https://discord.gg/ysq4ayTc83')
    
    @dev.command()
    async def output(self, ctx, *, cmd:str):
        paginator = commands.Paginator(max_size=1900, prefix='```powershell')
        paginator.add_line('$ {}\n'.format(cmd))
        interface = PaginatorInterface(ctx.bot, paginator, owner=ctx.author)
        await interface.send_to(ctx)
        for line in sp.getoutput(cmd).split('\n'):
            await asyncio.sleep(1)
            if not interface.closed:
                await interface.add_line('[stderr] {}'.format(line))
        await interface.add_line('\n[status] Output Code {}'.format(sp.getstatusoutput(cmd)[0]))
    
    @dev.command()
    async def remmessage(self, ctx, id:int):
        try:
            await (await ctx.fetch_message(id)).delete()
            await ctx.send('Successfully deleted ' + str(id))
        except discord.Forbidden:
            await ctx.send('I require manage messages permission to delete this message')
    
    @dev.command()
    async def clear(self, ctx, amount:int):
        def is_me(m):
            return m.author.id == self.bot.user.id
        
        purges = await ctx.channel.purge(limit=amount, check=is_me, bulk=False)
        await ctx.send(f"cleared {len(purges)} messages")
    
    @dev.command()
    async def blacklist(self, ctx, member:discord.Member):
        with open('./bans.json', 'r') as f:
            bans = json.load(f)
        
        bans[str(member.id)] = 'Yes'
        
        with open('./bans.json', 'w') as f:
            json.dump(bans, f, indent=4)
        
        await ctx.send('Successfully blacklisted {} from this bot'.format(member.display_name))
    
    @dev.command()
    async def whitelist(self, ctx, member:discord.Member):
        with open('./bans.json', 'r') as f:
            bans = json.load(f)
        
        del bans[str(member.id)]
        
        with open('./bans.json', 'w') as f:
            json.dump(bans, f, indent=4)
        
        await ctx.send('Successfully whitelisted {} from this bot'.format(member.display_name))
    
    @dev.command(hidden=True)
    async def movingTest(self, ctx):
        menu = games.TestMover(timeout=60.0, clear_reactions_after=True)
        await menu.start(ctx)
        await ctx.send('i swear to god Jm if you even press a button on this i will blacklist you')
    
    @commands.command(hidden=True)
    async def verify(self, ctx):
        if ctx.guild.name == 'The Good Guy Server':
            await ctx.message.delete()
            role_id = 758538458951843843
            role = get(ctx.guild.roles, id=role_id)
            await ctx.author.add_roles(role)
        elif ctx.guild.name != 'The Good Guy Server':
            await ctx.send('wrong guild')
    
    @dev.command(brief='Screenshots a webpage')
    async def scrn(self, ctx, *, url:str):
        warn = await ctx.channel.send('This may take some time...')
        await ctx.send(file=await self.utils.screenshot_web(url))
        await warn.delete()
    
    @dev.command(brief='Invoke a command')
    async def invoke(self, ctx, *args, **kwargs):
        args = [arg for arg in args]
        command = self.bot.get_command(args.pop(0))
        s = time.perf_counter()
        await command(ctx, *args, **kwargs)
        t = time.perf_counter()
        e = (t - s) * 1000
        await ctx.channel.send(f'Command {command.name} finished in {round(e, 6)}ms')
    
    @dev.command(hidden=True)
    async def paginatorTest(self, ctx, *args):
        argse = []
        for arg in args:
            if arg.startswith("discord.Embed("):
                eval(f'argse.append({arg})')
                continue
            argse.append(arg)
        ctx.choices = argse or [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        menu = PaginatorTest()
        return await menu.start(ctx)
    
    @dev.command()
    async def paginatorTestSecond(self, ctx, *args):
        paginator = commands.Paginator(max_size=1900, prefix='', suffix='')
        for arg in args:
            paginator.add_line(arg)
            paginator.add_line('\n'*(1898 - len(arg.split('\n'))))
        interface = PaginatorInterface(ctx.bot, paginator, owner=ctx.author)
        await interface.send_to(ctx)
    
    @dev.command()
    async def timeit(self, ctx, *, expression:str):
        s = time.perf_counter()
        eval(expression)
        t = time.perf_counter()
        e = round((t - s)*1000, 6)
        await ctx.send('Took {}ms'.format(e))
    
    @dev.command()
    async def sql(self, ctx, *, sql:str):
        if not sql.lower().startswith('select '):
            return_code = 1
            try:
                cur = self.bot.db.execute(sql)
                self.bot._conn.commit()
            except Exception as e:
                return_code = "0\n\nCheck console or logs for details"
                raise e
            name = sql.split()[0].upper()
            await ctx.send(name + " " + str(return_code))
        else:
            cur = self.bot.db.execute(sql)
            names = [description[0] for description in cur.description]
            result = cur.fetchall()
            await ctx.send('```sml\n' + tabulate.tabulate(result, names, tablefmt='pretty') + '\n```')
    
    @dev.group(invoke_without_command=True)
    async def errors(self, ctx):
        paginator = commands.Paginator(max_size=1900)
        cur = self.bot.db.execute('SELECT * FROM errors')
        result = cur.fetchall()
        results = []
        for res in range(len(result)):
            paginator.add_line(result[res][1] + ' - ' + result[res][2].replace('Command raised an exception: ', ''))
        interface = PaginatorEmbedInterface(ctx.bot, paginator, owner=ctx.author, embed=discord.Embed(color=0x2F3136, title='Errors Caught'))
        await interface.send_to(ctx)
    
    @errors.command()
    async def fix(self, ctx):
        entries = []
        if self.bot.db.execute('SELECT * FROM errors').fetchall() == []:
            return await ctx.send('You fixed 0 errors...')
        for entry in range(len(self.bot.db.execute('SELECT * FROM errors').fetchall())):
            entries.append(self.bot.db.execute('SELECT * FROM errors').fetchall()[entry][2])
        cur = self.bot.db.execute('DELETE FROM errors')
        self.bot._conn.commit()
        await ctx.send('Thanks for fixing {} error(s).'.format(len(entries)))
    
    @dev.command()
    async def code(self, ctx, *, code:str):
        await ctx.send(await self.utils.compute_code(code))
    
    @dev.command()
    async def reboot(self, ctx):
        with open('restart.bat', 'w') as f:
            f.write(f'taskkill /F /PID {os.getpid()}\npy bot.py')
        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')
        await ctx.send('brb')
        sp.call('restart.bat')
    
    @dev.command()
    async def priorityChange(self, ctx, user:discord.Member):
        if user.id in self.bot.owner_ids:
            self.bot.owner_ids.remove(user.id)
            return await ctx.send(f'User {user.name} has been removed as an owner of this bot')
        self.bot.owner_ids.add(user.id)
        await ctx.send(f'User {user.name} has been added as an owner of this bot')
    
    @dev.command()
    async def prefixless(self, ctx, toggle:bool):
        self.bot.prefixless = toggle
        await ctx.send('Changed.')
    
    @dev.command()
    async def pinger(self, ctx, object:typing.Union[discord.Member, discord.Role]):
        await ctx.send(object.mention)
    
    @dev.command()
    async def socket(self, ctx):
        paginator = commands.Paginator(max_size=1900)
        for k, v in self.bot.events_dispatched.items():
            paginator.add_line(f'{k:<30}{v}')
        interface = PaginatorEmbedInterface(ctx.bot, paginator, owner=ctx.author, embed=discord.Embed(color=0x2F3136, title='Socket'))
        await interface.send_to(ctx)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        emojis = []
        canRun = False
        for char in message.content.split(';;;'):
            if not ';;;' in message.content:
                return
            if not char == '':
                emoji = await self.utils.find(char, self.bot.emojis, key=lambda x: x.name)
                if emoji:
                    emojis.append((emoji[0], ';;;'+char))
                    canRun = True
                else:
                    return
        if canRun:
            content = message.content
            for emoji in emojis:
                content = content.replace(emoji[1], str(emoji[0]))
            await message.channel.send(content)
    
    @dev.command(name='exe')
    async def eval_async(self, ctx, *, code:str):
        self.env = {
                'ctx': ctx,
                'bot': self.bot,
                'utils': self.bot.utils,
                'code': code,
                'self': self,
                'guild': ctx.guild,
                'message': ctx.message,
                'author': ctx.author,
                '_': self._last_result,
                'async_execute': self.async_execute,
                'exe': ctx.command,
                'stdout': sys.stdout,
                'get_commands': CommandObjects(self.bot)
                }
        self.env.update({'env': self.env})
        for elem, item in self.env.items():
            setattr(self.env['exe'], elem, item)
        obj = await self.async_execute(code, self._last_result, self.env)
        return (await ctx.send(obj) if not obj in (None, '', discord.Embed, discord.File) else None) if len([a for a in str(obj)]) < 2000 else None
    
    @dev.command(name='exef')
    async def eval_async_file(self, ctx, *, filename:str):
        file = await self.bot.fakefiles.get_file(filename)
        code = file.code
        self.env = {
                'ctx': ctx,
                'bot': self.bot,
                'utils': self.bot.utils,
                'code': code,
                'self': self,
                'guild': ctx.guild,
                'message': ctx.message,
                'author': ctx.author,
                '_': self._last_result,
                'async_execute': self.async_execute,
                'exef': ctx.command,
                'get_commands': CommandObjects(self.bot),
                'filename': filename
                }
        self.env.update({'env': self.env})
        for elem, item in self.env.items():
            setattr(self.env['exef'], elem, item)
        obj = await self.async_execute(code, self._last_result, self.env)
        return (await ctx.send(obj) if not obj in (None, '', discord.Embed, discord.File) else None) if len([a for a in str(obj)]) < 2000 else None
    
    @dev.command()
    async def tio(self, ctx, language, *, code:str):
        site = Tio()
        request = TioRequest(language if language != "py" else "python3", code)
        try:
            result = site.send(request)
        except IndexError:
            await ctx.send(f'`{language}` is not available')
        else:
            if not result.error:
                await ctx.send(f'```{language}\n{result.result}\n```')
            else:
                await ctx.send(f'```{language}\n{result.error}\n```')
    
    @dev.command()
    async def bugs(self, ctx):
        bugs = [c[0] for c in self.bot.db.execute('SELECT bug FROM bugs')]
        paginator = commands.Paginator(max_size=1900, prefix='', suffix='')
        for i, n in enumerate(bugs):
            paginator.add_line(f'{i+1}. {n}')
        interface = PaginatorEmbedInterface(ctx.bot, paginator, owner=ctx.author, embed=discord.Embed(title='Bugs'))
        await interface.send_to(ctx)
        
    @dev.group()
    async def fakefiles(self, ctx):
        pass
    
    @fakefiles.command()
    async def setcurrent(self, ctx, name):
        await self.bot.fakefiles.setcurrent(name)
        await ctx.send(f'Successfully changed current file to "{name}"')
    
    @fakefiles.command()
    async def set(self, ctx, code):
        await self.bot.fakefiles.set(code)
        await ctx.send(f'Succesfully set code of current file to `{code}`')
    
    @fakefiles.command()
    async def append(self, ctx, code):
        await self.bot.fakefiles.add(code)
        await ctx.send(f'Succesfully added `{code}` to code of current file')
    
    @fakefiles.command()
    async def add(self, ctx, name, code):
        await self.bot.fakefiles.new_file(name, code)
        await ctx.send(f'Successfully added new file named "{name}"')
    
    @fakefiles.command()
    async def rem(self, ctx, code):
        await self.bot.fakefiles.rem(code)
        await ctx.send(f'Successfully removed `{code}` from current file')
    
    @fakefiles.command()
    async def delete(self, ctx, name):
        await self.bot.fakefiles.delete(name)
        await ctx.send(f'Successfully deleted "{name}" from list of files')
    
    @fakefiles.command()
    async def getfile(self, ctx, name):
        file = await self.bot.fakefiles.get_file(name)
        await ctx.send(f'```\n{file.code}\n```')
    
    @dev.command()
    async def regex(self, ctx, *, flags:RegexFlags):
        resp = await self.bot.utils.regex(flags.match, flags.subject)
        await ctx.send(resp)

async def async_setup(bot):
    await bot.add_cog(Admin(bot))

def setup(bot):
    return async_setup(bot)
    bot.add_cog(Admin(bot))
