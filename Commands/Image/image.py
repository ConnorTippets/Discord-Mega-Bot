import discord
from discord.ext import commands
from discord.ext.commands import BadArgument, UserConverter, MemberConverter
from asyncdagpi import ImageFeatures
from PIL import Image as imager
from PIL import ImageDraw, ImageFont
from Pillow.hackerman import hackerman as hackerman_orig
from Pillow.filters import emboss as emboss_orig
from Pillow.filters import blur as blur_orig
from Pillow.polygons import rectangle as rect_orig
from Pillow.models import caption as caption_orig
from Pillow.models import kindle as kindle_orig
from Pillow.models import display as display_orig
from Pillow.google import google as google_orig
from Pillow.polygons import ellipse as ell_orig
import Utils
import io
import textwrap
import typing
import time
import string
import aiohttp

def occuranceof(query, input):
    return len([query for a in input if a == query])

def highestof(input):
    highest = []
    for x in input:
        if len(x) > len(highest):
            highest = x
    return highest

class URLConverter(commands.Converter):
    async def convert(self, ctx, x):
        ik = False
        if not x:
                if len(ctx.message.attachments) > 0:
                    x = ctx.message.attachments[0].url
                    ik = True
                else:
                    x = ctx.author.avatar.url
                    ik = True
        try:
            _ = await MemberConverter().convert(ctx, x)
            i = True
        except:
            try:
                _ = await UserConverter().convert(ctx, x)
                i = True
            except:
                i = False
        if i and not ik:
            try:
                x = _.avatar.url
            except AttributeError:
                raise BadArgument('User does not have a detectable picture (default avatar maybe?)')
        try:
            async with aiohttp.ClientSession() as cs:
                async with cs.get(x) as r:
                    resp = await r.read()
                    k = r.status
        except:
            k = 0
        if (not type(x) == str) or (not k == 200):
            raise BadArgument('Cannot convert argument into url')
        return x

class Image(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.last_images = []
    
    @commands.command(aliases=['colours'])
    async def colors(self, ctx, member:discord.Member=None):
        if member is None:
            member = ctx.author
        
        url = member.avatar.with_format("png").with_size(1024).url
        img = await self.bot.dag.image_process(ImageFeatures.colors(), url)
        await ctx.send(file = discord.File(fp=img.image,filename=f"pixel.{img.format}"))
    
    @commands.command()
    async def wanted(self, ctx, member:discord.Member=None):
        if member is None:
            member = ctx.author
        warn_msg = 'the dagpi wanted endpoint has a flaw which makes it very slow to compute' if ctx.author.id in self.bot.owner_ids else 'This may take some time'
        warn = await ctx.send(warn_msg)
        url = member.avatar.with_format("png").with_size(1024).url
        img = await self.bot.dag.image_process(ImageFeatures.wanted(), url)
        try:
            await warn.delete()
        except:
            pass
        finally:
            await ctx.send(file = discord.File(fp=img.image,filename=f"pixel.{img.format}"))
    
    @commands.command()
    async def hackerman(self, ctx, *, text="supply some text bish"):
        await ctx.send(file=discord.File(await self.bot.loop.run_in_executor(None, hackerman_orig, text), "DMB_Hackerman_Result.png"))
    
    @commands.command()
    async def emboss(self, ctx, *, author:discord.Member=None):
        author = author or ctx.author
        if ctx.message.attachments:
            author = type('something',(),{'avatar': type('something_else',(),{'url': ctx.message.attachments[0].url})})
        elif ctx.message.reference:
            if ctx.message.reference.resolved.attachments:
                author = type('something',(),{'avatar': type('something_else',(),{'url': ctx.message.reference.resolved.attachments[0].url})})
        resp = await self.bot.utils.imaging_api('avatar/emboss', avatar=(author.url if not hasattr(author, 'avatar') else author.avatar.url))
        if resp == 'api_off':
            raise ctx.CommandError('DMB API is currently off, nothing you can control. Try again later.')
        await ctx.send(file=discord.File(resp, 'DMB_Emboss_Result.png'))
    
    @commands.command()
    async def blur(self, ctx, *, author:discord.Member=None):
        author = author or ctx.author
        if ctx.message.attachments:
            author = type('something',(),{'avatar': type('something_else',(),{'url': ctx.message.attachments[0].url})})
        elif ctx.message.reference:
            if ctx.message.reference.resolved.attachments:
                author = type('something',(),{'avatar': type('something_else',(),{'url': ctx.message.reference.resolved.attachments[0].url})})
        resp = await self.bot.utils.imaging_api('avatar/blur', avatar=(author.url if not hasattr(author, 'avatar') else author.avatar.url))
        if resp == 'api_off':
            raise ctx.CommandError('DMB API is currently off, nothing you can control. Try again later.')
        await ctx.send(file=discord.File(resp, 'DMB_Blur_Result.png'))
    
    @commands.command()
    async def rectangle(self, ctx, x1:int, y1:int, x2:int, y2:int, color:str="green"):
        im = None
        if ctx.message.attachments:
            im = io.BytesIO(await ctx.message.attachments[0].read())
        elif ctx.message.reference:
            if ctx.message.reference.resolved.attachments:
                im = io.BytesIO(await ctx.message.reference.resolved.attachments[0].read())
        resp = (await self.bot.utils.imaging_api('poly/rectangle', x1=x1, y1=y1, x2=x2, y2=y2, color=color, image=im) if im else await self.bot.utils.imaging_api('poly/rectangle', x1=x1, y1=y1, x2=x2, y2=y2, color=color))
        if resp == 'api_off':
            raise ctx.CommandError('DMB API is currently off, nothing you can control. Try again later.')
        await ctx.send(file=discord.File(resp, 'DMB_Rectangle_Result.png'))
    
    @commands.command()
    async def isod(self, ctx, *, input:str):
        gif = (True if input.split(' ')[-1] == 'gif' else False)
        width, height = len(highestof(input.replace('-', '\n').split('\n'))), occuranceof('\n', input)+1
        params = {'input':input}
        s = time.perf_counter()
        if not gif:
            resp = await self.bot.utils.imaging_api('isod2d', input=input)
        else:
            resp = await self.bot.utils.imaging_api('isod2d', input=input.replace(' gif', ''), gif=True)
        if resp == io.BytesIO() and gif:
            return await ctx.send('Gif block count exceeded 350')
        if resp == io.BytesIO() and not gif:
            return await ctx.send('Block count exceeded 750')
        if resp == 'api_off':
            raise ctx.CommandError('DMB API is currently off, nothing you can control. Try again later.')
        e = time.perf_counter()
        string_reviewed = ''.join([a for a in string.printable if not (a == "1" or a == "2" or a == "3" or a == "4" or a == "5" or a == "6" or a == "7")])
        block_num = input
        for a in string_reviewed:
            block_num = block_num.replace(a, "")
        block_num = len(block_num)
        time_num = e - s
        if not gif:
            await ctx.send(((f'Rendered `{block_num}` blocks ' if block_num != 1 else 'Rendered `1` block ') + (f'in `{time_num}` seconds' if time_num != 1 else 'in `1` second')) + f'; `{width}x{height}`', file=discord.File(resp, 'DMB_ISOD_Result.png'))
        else:
            await ctx.send(((f'Rendered `{block_num}` blocks ' if block_num != 1 else 'Rendered `1` block ') + (f'in `{time_num}` seconds' if time_num != 1 else 'in `1` second')) + f'; `{width}x{height}`', file=discord.File(resp, 'DMB_ISOD_Result.gif'))

    @commands.command()
    async def pixelate(self, ctx, url:URLConverter=None, size:commands.Range[int, 1, 128]=64, outline:commands.Range[int, 0, 15]=0):
        if url == None:
            url = ctx.author.avatar.url
        resp = await self.bot.utils.imaging_api('itid', url=url, size=size, outline=outline)
        await ctx.send(file=discord.File(resp, 'DMB_ITID_Result.png'))
    
    @commands.command()
    async def caption(self, ctx, author=None, text:str="you either didn't give any text or you forgot to add author param and it converted to user :)"):
        _ = discord.utils.get(self.bot.users, name=author)
        if not _:
            text = author
            author = ctx.author
        else:
            author = _
        await ctx.send(file=discord.File(await (await self.bot.loop.run_in_executor(None, caption_orig, author, text)), 'DMB_Caption_Result.png'))
    
    @commands.command()
    async def kindle(self, ctx, *, member:typing.Optional[discord.Member]=None):
        image = (ctx.message.attachments[0] if len(ctx.message.attachments)>0 else None) or (member.avatar if not member == None else None) or ctx.author.avatar
        await ctx.send(file=discord.File(await (await self.bot.loop.run_in_executor(None, kindle_orig, image)), 'DMB_Kindle_Result.png'))
    
    @commands.command()
    async def google(self, ctx, *, text:str="supply some text bish"):
        text = ' '.join([a for a in (text if not len(text) > 73 else text[(len(text)-73):]).split('\n')])
        buffer = await self.bot.loop.run_in_executor(None, google_orig, text)
        await ctx.send(file=discord.File(buffer, 'DMB_Google_Result.png'))

    @commands.command()
    async def display(self, ctx, member:typing.Optional[discord.Member]=None, *, text:str=None):
        member = member or ctx.author
        if not text:
            for s in member.activities:
                if isinstance(s, discord.CustomActivity):
                    await ctx.send(file=discord.File(await (await self.bot.loop.run_in_executor(None, display_orig, s.name, member)), 'DMB_Display_Result.png'))
        else:
            await ctx.send(file=discord.File(await (await self.bot.loop.run_in_executor(None, display_orig, text, member)), 'DMB_Display_Result.png'))

async def async_setup(bot):
    await bot.add_cog(Image(bot))

def setup(bot):
    return async_setup(bot)
    bot.add_cog(Image(bot))
