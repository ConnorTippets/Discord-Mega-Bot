import discord
from discord.ext import commands
from discord.ext import ui
from discord.utils import get, find

def oauth2link():
    link = discord.utils.oauth_url(client_id=741624868591763487, permissions=discord.Permissions(permissions=8))
    e = discord.Embed(title='Invite DMB To your server', description=f'[:robot: Invite Link]({link})', color=random.randint(100000, 999999))
    return e

class Server(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief='Who has this role?')
    async def whoHas(self, ctx, *, rolename:str):
        role = get(ctx.guild.roles, name=rolename)
        if not role:
            raise ctx.CommandError('{0} is not a role.'.format(rolename, 0))
        await ctx.send(',\n'.join([a.name for a in role.members]))
    
    @commands.command(brief='Shows info on the current server')
    async def serverInfo(self, ctx, *, guild=None):
        guild = get(self.bot.guilds, name=guild) or ctx.guild
        infos = []
        info = discord.Embed(color=0x2F3136)
        infos.append(info)
        infos.append(discord.Embed(color=0x2F3136))
        info.set_author(name=guild)
        if hasattr(guild.icon, "url"):
            info.set_thumbnail(url=guild.icon.url)
        info.add_field(name='Created At', value=guild.created_at)
        info.add_field(name='Member Count', value=len(guild.members), inline=False)
        info.add_field(name='Server ID', value=guild.id, inline=False)
        info.add_field(name='Server Owner', value=guild.owner.mention, inline=False)
        info.add_field(name=f'Total Text Channels: **{len(guild.text_channels)}**', value=', '.join([a.name for a in guild.text_channels[:6]])+', etc...', inline=False)
        info.add_field(name=f'Total Bots: **{len([a.name for a in guild.members if a.bot])}**', value=', '.join([a.name for a in guild.members if a.bot][:6])+', etc...', inline=False)
        info.add_field(name=f'Total Users: **{len([a.name for a in guild.members if not a.bot])}**', value=', '.join([a.name for a in guild.members if not a.bot][:6])+', etc...', inline=False)
        infos[1].add_field(name=f'Total Members: **{len(guild.members)}**', value=', '.join([a.name for a in guild.members][:6])+', etc...', inline=False)
        infos[1].add_field(name=f'Total Roles: **{len([a for a in guild.roles if not a.name == "@everyone"])}**', value=', '.join([a.name for a in guild.roles[:7] if not a.name == "@everyone"])+', etc...', inline=False)
        await ctx.send(embeds=infos)

async def async_setup(bot):
  await bot.add_cog(Server(bot))

def setup(bot):
  return async_setup(bot)
  bot.add_cog(Server(bot))
