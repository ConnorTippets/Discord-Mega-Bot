import discord
from discord.ext import commands
from discord import utils
import random
from datetime import datetime as dt
from asyncio import sleep
import time
import inspect
import os
from discord.ext import flags
from discord import FFmpegPCMAudio, FFmpegOpusAudio, opus
from youtube_dl import YoutubeDL
import ctypes
import praw
import sys
import humanize
import mystbin
import aiohttp
import datetime
import urllib
import requests
import string
from bs4 import BeautifulSoup
import difflib
from jishaku.paginators import WrappedPaginator, PaginatorEmbedInterface
import io, expr

def replacer(text):
    output = []
    for k in text.lower():
        if k in string.ascii_lowercase:
            output.append(f':regional_indicator_{k}:')
        if k == " ":
            output.append(" ")
        if k == "!":
            output.append(":exclamation:")
        if k.isdigit():
            output.append(f":{humanize.apnumber(k)}:")
        else:
            pass
    return "".join(output)

def scrape_google(query):
    query = query.replace(' ', '+')
    url = f"https://google.com/search?q={query}"
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
    headers = {"user-agent": USER_AGENT}
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.content, "html.parser")
        results = []
        for g in soup.find_all('div', class_='r'):
            anchors = g.find_all('a')
            if anchors:
                link = anchors[0]['href']
                item = {
                    "link": link
                }
                results.append(item)
        return results
    
async def getReddit(ctx, subreddit):
    async with aiohttp.ClientSession() as c:
        async with c.get(f'https://www.reddit.com/r/{subreddit}/hot.json') as resp:
            json = (await resp.json())['data']['children']
            try:
                choice = random.choice(json)
            except IndexError:
                return discord.Embed(title='Unknown / Empty Subreddit', color=0x2F3136)
            embed = discord.Embed(title=choice['data']['title'], color=0x2F3136, url=f'https://reddit.com{choice["data"]["permalink"]}')
            embed.set_author(name=f'u/{choice["data"]["author_fullname"]}')
            if choice['data'].get('url') and choice['data']['is_video']:
                embed.description = f"[Video Included]({choice['data']['url']})"
            elif choice['data'].get('url_overridden_by_dest'):
                embed.set_image(url=choice['data']['url_overridden_by_dest'])
            else:
                embed.description = choice['data']['selftext']
            embed.set_footer(text=f'ID: {choice["data"]["id"]}')
    if choice['data']['over_18'] and not ctx.channel.is_nsfw():
        return discord.Embed(title='Post must be looked at in nsfw channel.', color=0x2F3136)
    else:
        return embed
    
def usage_for(bot, name):
    command = bot.get_command(name)
    if not command.aliases:
        if not command.root_parent:
            return f"{command.name} {command.signature}", command.brief
        else:
            return f"{command.root_parent.name} {command.name} {command.signature}", command.brief
    else:
        if not command.root_parent:
            return f"{command.name}/{'/'.join(command.aliases)} {command.signature}", command.brief
        else:
            return f"{command.root_parent.name} {command.name}/{'/'.join(command.aliases)} {command.signature}", command.brief

def usages_for(bot, name):
    command = bot.get_command(name)
    if not command.aliases:
        if not isinstance(command, commands.Group):
            if not command.root_parent:
                return f"{command.name} {command.signature}", command.brief
            else:
                return f"{command.root_parent.name} {command.name} {command.signature}", command.brief
        else:
            return f"{command.name} {command.signature}\n" + '\n'.join([f"{command.root_parent.name} {command.name} {command.signature}" for command in command.commands]), command.brief
    else:
        return f"{command.name}|{'|'.join(command.aliases)} {command.signature}", command.brief

def oauth2link():
    link = discord.utils.oauth_url(client_id=741624868591763487, permissions=discord.Permissions(permissions=8))
    e = discord.Embed(title='Invite DMB To your server', description=f'[:robot: Invite Link]({link})', color=random.randint(100000, 999999))
    return e

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.command_stats = {}
        self.bot.afk = {}
        self.bot.usages_for = usages_for
        self.usage_for = usage_for
        self.categories = {list(self.bot.cogs).index(i)+1: self.bot.cogs[i] for i in self.bot.cogs}
    
    async def sendMessage(self, messageObj):
        hasAttachments = bool(messageObj.attachments)
        hasEmbeds = bool(messageObj.embeds)
        hasContent = messageObj.content is not None
        if hasContent and all([not hasAttachments, not hasEmbeds]):
            await messageObj.reply(messageObj.content, mention_author = False)
        elif hasContent and not hasAttachments and hasEmbeds:
            await messageObj.reply(messageObj.content, embed=messageObj.embeds[0], mention_author = False)
        elif hasContent and hasAttachments and not hasEmbeds:
            await messageObj.reply(messageObj.content, files=[await att.to_file() for att in messageObj.attachments], mention_author = False)
        elif hasContent and all([hasAttachments, hasEmbeds]):
            await messageObj.reply(messageObj.content, files=[await att.to_file() for att in messageObj.attachments], embed=messageObj.embeds[0], mention_author = False)
        elif not hasContent and hasAttachments and not hasEmbeds:
            await messageObj.reply(files=[await att.to_file() for att in messageObj.attachments], mention_author = False)
        elif not hasContent and not hasAttachments and hasEmbeds:
            await messageObj.reply(embed=messageObj.embeds[0], mention_author = False)
        elif not hasContent and all([hasAttachments, hasEmbeds]):
            await messageObj.reply(files=[await att.to_file() for att in messageObj.attachments], embed=messageObj.embeds[0], mention_author = False)

    @commands.command(brief='A command that lets you be able to make the bot say anything')
    async def echo(self, ctx, *, content:commands.clean_content):
        await ctx.send(content)
    
    @commands.command(brief='Generates a random color and shows it to you in the form of an embed.')
    async def rcolor(self, ctx):
        r = discord.Color.random()
        e = discord.Embed(title='Random Color', description=r, color=r)
        await ctx.send(embed=e)
    
    @commands.command(brief='Shows help for this bot', invoke_without_command=True)
    async def help(self, ctx, query:str=None):
      if not query:
          helpc = discord.Embed(color=0x2F3136, title='Help Categories')
          cogs = [name for name in self.bot.cogs]
          cogs.remove('Jishaku')
          cogs.remove('Admin')
          cogs.remove("Imaging")
          categories = '\n'.join(cogs)
          helpc.add_field(name='Categories', value=f"""
```
{categories}
```
Please choose one using {ctx.prefix}help <category name>.
          """)
          await ctx.send(embed=helpc)
      else:
          maybe_cog = self.bot.get_cog(query.lower().capitalize())
          if not maybe_cog and query.lower() == 'api':
              maybe_cog = self.bot.get_cog('API')
          if maybe_cog:
              if maybe_cog.qualified_name == 'Admin' and not await ctx.bot.is_owner(ctx.author):
                  await ctx.send('Access Denied')
                  return
              else:
                  commands = '\n'.join([command.name if not command.root_parent else f'{command.root_parent.name} {command.name}' for command in [command for command in maybe_cog.__cog_commands__]])
                  e = discord.Embed(color=0x2F3136, title=f'{maybe_cog.qualified_name}', description=f'{commands}\n\nYou can use {ctx.prefix}help <command name> to get help on a command')
                  await ctx.send(embed=e)
          else:
              try:
                  command = self.bot.get_command(query)
                  try:
                      if command.cog.qualified_name == 'Admin' and not await ctx.bot.is_owner(ctx.author):
                          await ctx.send('Access Denied.')
                          return
                  except:
                      pass
                  embed = discord.Embed(color=0x2F3136, description=usage_for(self.bot, query)[1])
                  embed.set_author(name=usage_for(self.bot, query)[0])
                  if isinstance(command, discord.ext.commands.Group):
                      subcommands = [f'`{c.name}`' for c in command.commands]
                      embed.add_field(name='Subcommands', value=', '.join(subcommands))
                  await ctx.send(embed=embed)
              except AttributeError as e:
                  c = difflib.get_close_matches(query, [m.name for m in self.bot.commands])
                  await ctx.send(f'That isn\'t a command. Did you mean {c[0]}?' if c else 'That isn\'t a command.')
    
    @commands.command(brief='Shows an OAuth Invite for the bot')
    async def invite(self, ctx):
        await ctx.send(embed = oauth2link())
    
    @commands.command(brief='Shows you the bot\'s ping')
    async def ping(self, ctx):
        latency = round((self.bot.latency * 1000), 6)
        start = time.perf_counter()
        message = await ctx.send("l")
        end = time.perf_counter()
        duration = (end - start) * 1000
        e = discord.Embed(title=':ping_pong: Pong!', color=0x2F3136)
        e.add_field(name='Websocket Latency', value="{}ms".format(latency))
        e.add_field(name='Typing Latency', value="{:.2f}ms".format(duration))
        e.set_thumbnail(url=self.bot.user.avatar.url)
        await message.edit(content="", embed=e)
    
    @commands.command(brief='Hi!')
    async def hello(self, ctx):
        await ctx.send(':wave: Hi, I\'m DMB (Discord Mega Bot)!')
    
    @commands.command(name='random', brief='Generates a random number between whatever you want.')
    async def _random(self, ctx, minimum : int=0, maximum : int=2147483647):
        randomnumber = random.randint(minimum, maximum)
        await ctx.send(str(randomnumber) + " was chosen")
    
    @commands.command(brief='Technical Info about the bot')
    async def technicalInfo(self, ctx):
        e = discord.Embed(color=0x2F3136)
        e.set_footer(text='@Copyright 2020 Connor Tippets')
        e.set_thumbnail(url=self.bot.user.avatar.url)
        e.set_author(name='Technical Info', icon_url=self.bot.user.avatar.url)
        e.add_field(name='Discord.py Release Level: ', value=f'{discord.version_info.releaselevel}', inline=False)
        e.add_field(name='Discord.py Release: ', value=f'{str(discord.__version__)}', inline=False)
        e.add_field(name='Python Release: ', value='{}.{}.{}'.format(sys.version_info[0], sys.version_info[1], sys.version_info[2]))
        await ctx.send(embed=e)
    
    @commands.command(brief='Info about the bot')
    async def info(self, ctx):
        bot_user = self.bot.user
        bot_info = await self.bot.application_info()
        e = discord.Embed(color=0x2F3136)
        e.set_footer(text='@Copyright 2020 Connor Tippets')
        e.set_thumbnail(url=bot_user.avatar.url)
        e.set_author(name='Bot Info', icon_url=bot_user.avatar.url)
        e.add_field(name='Name: ', value=f'{bot_info.name}', inline=False)
        e.add_field(name='Id: ', value=f'{bot_info.id}', inline=False)
        e.add_field(name='Bot Creator: ', value=f'{bot_info.owner.mention}', inline=False)
        e.add_field(name='Default Prefix: ', value='::', inline=False)
        e.add_field(name='Servers: ', value=len(self.bot.guilds), inline=False)
        e.add_field(name='Users: ', value=len(self.bot.users), inline=False)
        e.add_field(name='Credit: ', value='I made most of it myself, but i\'ll give credit where credit is due:', inline=False)
        e.add_field(name='Danny', value='https://github.com/Rapptz/RoboDanny\nhttps://github.com/Rapptz/discord.py', inline=True)
        e.add_field(name='Discord.py Server members', value='https://discord.gg/dpy', inline=True)
        e.add_field(name='And of course, all my friends.', value='None of this would\'ve existed without them.', inline=True)
        await ctx.send(embed=e)
    
    @commands.command(aliases=['connect'], brief='Makes the bot join a VC')
    async def join(self, ctx):
        channel = ctx.author.voice.channel
        if not channel:
            await ctx.send("You are not connected to a voice channel")
            return
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        voice = await channel.connect()
        await ctx.send('Connected!')
    
    @commands.command(aliases=['disconnect'], brief='Makes the bot leave a VC')
    async def leave(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        await voice.disconnect()
        await ctx.send('Disconnected!')
    
    @commands.command(brief='Makes the bot play music in a VC')
    async def play(self, ctx, *, url):
        await ctx.send("OMFG THIS COMMAND DOESN'T WORK I AM GOING INSANE WHY CAN'T IT JUST ENCODE ITSELF AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA -Con, the main \"mechanic\" of this bot going insane trying to figure out how opus library encoding works. SEND HELP")
        return
        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        
        if voice is None:
            await ctx.send('Not Connected to VC! Connecting....')
            channel = ctx.author.voice.channel
            if not channel:
                await ctx.send("You are not connected to a voice channel")
                return
            voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
            voice = await channel.connect()
            await ctx.send('Connected!')
            voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        else:
            if not voice.is_playing():
                    with YoutubeDL(YDL_OPTIONS) as ydl:
                        print('getting video')
                        if not url.startswith('https://'):
                            info = ydl.extract_info(f"ytsearch:{url}", download=False)
                        else:
                            info = ydl.extract_info(url, download=False)
                    print('getting url after getting video')
                    if info.get('formats'):
                        URL = info['formats'][0]['url']
                    else:
                        URL = info['entries'][0]['formats'][0]['url']
                    print('playing music')
                    voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
                    voice.is_playing()
                    print('stopped???')
            else:
                await ctx.send("Already playing song")
                return
    
    @commands.command(brief='Stops the playing music in a VC, doesn\'t if there isn\'t any playing')
    async def stop(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            voice.stop()
            await ctx.send('Stopped playing music!')
        else:
            await ctx.send('Not playing music. Can\'t stop!')
    
    @commands.command(brief='Makes the bot do a calculation, using safe evaluation')
    async def math(self, ctx, *, expression:str):
        evaluations = [str(a) for a in [expr.evaluate(a) for a in expression.split('\n')] if not a is None]
        x = await ctx.send('\n'.join(evaluations)) if evaluations else None
    
    @commands.command(brief='Gets a meme from r/memes or r/dankmemes')
    async def meme(self, ctx):
        async with ctx.typing():
            await ctx.reply(embed=await getReddit(ctx, random.choice(['memes', 'dankmemes'])))
    
    @commands.command(brief='Gets a reddit post from the subreddit specified')
    async def reddit(self, ctx, subreddit):
        async with ctx.typing():
            await ctx.reply(embed=await getReddit(ctx, subreddit))
    
    @commands.command(brief='Posts something to mystbin')
    async def mystbin(self, ctx, syntax:str, *, data:str):
        paste = await self.bot.mystbin.post(data, syntax=syntax)
        await ctx.send(str(paste))
    
    @commands.command(brief='Gets something from mystbin')
    async def getbin(self, ctx, id):
        try:
            get_paste = await self.bot.mystbin.get(f"https://mystb.in/{id}")
            e = discord.Embed(title=f"Is this good?", description=f"The content is shown here:  [link]({get_paste.url})", color=0x2F3136)
            await ctx.send(embed=e)
        except mystbin.BadPasteID:
            return await ctx.send(f"Hmmm.. {id} isn't found, try again?")

    @commands.command(name='source', brief='Source code for commands', aliases=['src'])
    async def sources(self, ctx, *, command:str=None):
        if not command:
            raise ctx.CommandError('Please supply a command to get the source of.')
        x = self.bot.get_command(command)
        if not x:
            raise ctx.CommandError('Unknown command.')
        await ctx.send(file=discord.File(io.BytesIO(bytes(inspect.getsource(x.callback), encoding='utf-8')), f'{x.cog.__module__.split(".")[-1]}.py'))
    
    @commands.command(brief='Finds the average of numbers')
    async def avg(self, ctx, *args):
        values = [int(a) for a in args]
        await ctx.send('Average of `{}`: {}'.format(values, round(sum(values) / len(values))))
    
    @commands.command(brief='Computes code')
    async def code(self, ctx, *, code:str):
        await ctx.send(await self.bot.utils.compute_code(code))
    
    @commands.command(brief='Privacy Policy for this bot, required by discord ToS')
    async def privacy(self, ctx):
        embed = discord.Embed(color=0x2F3136, description='1. What data do you collect?\nI only collect about your user id and name\n\n2. Why do you need the data?\nI collect them for things like todo command\n\n3. How do you use the data?\nI use them to identify the discord user\n\n4. Who do you share your collected data with?\nI share the data with no one.\n\n5. How can users contact you if they have concerns about your bot?\nIf you have concerns about my bot, contact me on discord (info in bot info command)\n\n6. How can users have that data removed?\nIf you wish to remove your data, either contact me, or use the commands remove command (if it has one).')
        embed.set_author(icon_url=ctx.author.avatar.url, name='Privacy Policy')
        await ctx.send(embed=embed)
    
    @commands.command(brief='Shows all the bots emojis')
    async def emojis(self, ctx):
        paginator = WrappedPaginator(max_size=1900, prefix='', suffix='')
        for emoji in self.bot.emojis:
            paginator.add_line(f'{str(emoji)} - `{str(emoji)}`')
        interface = PaginatorEmbedInterface(ctx.bot, paginator, owner=ctx.author, embed=discord.Embed(title='Emojis', color=0x2F3136))
        await interface.send_to(ctx)
    
    @commands.command(brief='Switches your text to the emoji version of it')
    async def bigtext(self, ctx, *, text):
        await ctx.send(replacer(text))
    
    @commands.command(brief='Sends the content of the message you replied to')
    async def repliersend(self, ctx):
      reference = ctx.message.reference
      if not reference:
          return await ctx.send('You didn\'t reply to a message!')
      else:
          message = reference.resolved
          await self.sendMessage(message)
        

async def async_setup(bot):
  await bot.add_cog(General(bot))

def setup(bot):
  return async_setup(bot)
  bot.add_cog(General(bot))
