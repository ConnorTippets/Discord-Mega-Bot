import discord
from discord.ext import commands
import random
from discord.utils import get
from jishaku.paginators import PaginatorEmbedInterface

class Member(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(brief='Shows you the avatar of the person you choose, it will be you if you don\'t choose one', aliases=['av'])
    async def avatar(self, ctx, *, member:discord.Member=None):
        member = member or ctx.author
        e = discord.Embed(color=0x2F3136)
        e.set_image(url=member.avatar.url)
        await ctx.send(embed=e)
    
    @commands.command(brief='Shows you info on the person you choose, you if none chosen')
    async def whoIs(self, ctx, member:discord.Member=None):
        member = member or ctx.author
        e = discord.Embed(color=0x2F3136)
        e.set_footer(text='@Copyright 2020 Connor Tippets')
        e.set_thumbnail(url=member.avatar.url)
        e.set_author(name=member.name, icon_url=member.avatar.url)
        e.add_field(name='Nickname/Name: ', value=f'{member.display_name}', inline=False)
        e.add_field(name='Id: ', value=f'{member.id}', inline=False)
        e.add_field(name='Bot?: ', value=f'{member.bot}', inline=False)
        e.add_field(name='Tag: ', value=f'{member.discriminator}', inline=False)
        e.add_field(name=f'Total Roles: **{len([a for a in member.roles if not a.name == "@everyone"])}**', value=', '.join([a.name for a in member.roles if not a.name == "@everyone"][:6])+', etc...', inline=False)
        await ctx.send(embed=e)
    
    @commands.command(brief='Shows people with the discriminator specified')
    async def discrim(self, ctx, discrim:str):
        embed = discord.Embed(color=0x2F3136)
        people = [str(member) for member in self.bot.users if member.discriminator == discrim]
        paginator = commands.Paginator(max_size=1900, prefix='```py')
        for person in people:
            paginator.add_line(person)
        interface = PaginatorEmbedInterface(ctx.bot, paginator, owner=ctx.author, embed=embed)
        await interface.send_to(ctx)

async def async_setup(bot):
  await bot.add_cog(Member(bot))

def setup(bot):
  return async_setup(bot)
  bot.add_cog(Member(bot))
