import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(brief='Warns the person chosen')
    @has_permissions(kick_members=True)
    async def warn(self, ctx, member : discord.Member, *, reason='placeholder'):
        await ctx.send(member.mention + ' has been warned for the reason of ' + reason)
        await member.send('You were warned in {} with the reason of {}'.format(ctx.guild.name, reason))
    
    @commands.command(brief='Clears the amount of messages you choose from the channel')
    @has_permissions(manage_messages=True)
    async def clear(self, ctx, clear_amount=5):
        try:
            clear_amount = clear_amount + 1
            new_clear_amount = clear_amount - 1
            if new_clear_amount != 1:
                if new_clear_amount > 250:
                    await ctx.send('Error Code 007: Max clear amount is 250')
                elif new_clear_amount < 250:
                    await ctx.channel.purge(limit=clear_amount)
                    await ctx.send(f':thumbsup: {new_clear_amount} messages have been cleared')
                elif new_clear_amount == 250:
                    await ctx.channel.purge(limit=clear_amount)
                    await ctx.send(f':thumbsup: {new_clear_amount} messages have been cleared')
            elif new_clear_amount == 1:
                await ctx.message.delete()
                await ctx.send(f':thumbsup: {new_clear_amount} message have been cleared')
        except:
            await ctx.send('I have insufficient perms to do so.')
    
    @commands.command(brief='Kicks the person chosen')
    @has_permissions(kick_members=True)
    async def kick(self, ctx, member : discord.Member, *, reason=None):
        try:
            await member.kick(reason=reason)
            await ctx.send(f"{member} has been kicked by {ctx.author} for the reason of {reason}")
            await member.send('You were kicked in {} for the reason of {}'.format(ctx.guild.name, reason))
        except:
            await ctx.send('I have insufficient perms to do so.')
    
    @commands.command(brief='Bans the person chosen')
    @has_permissions(ban_members=True)
    async def ban(self, ctx, member : discord.Member, *, reason=None):
        try:
            await member.ban(reason=reason)
            await ctx.send(f"{member} has been banned by {ctx.author} for the reason of {reason}")
            await member.send("You were banned in {} for the reason of {}".format(ctx.guild.name, reason))
        except:
            await ctx.send('I have insufficient perms to do so.')
    
    @commands.command(brief='Unbans the person chosen')
    @has_permissions(ban_members=True)
    async def unban(self, ctx, *, member_id:int):
        try:
            object = discord.Object(member_id)
            await ctx.guild.unban(object)
            await ctx.send('Unbanned {}'.format(member_id))
        except:
            await ctx.send('I have insufficient perms to do so.')

async def async_setup(bot):
  await bot.add_cog(Moderation(bot))

def setup(bot):
  return async_setup(bot)
  bot.add_cog(Moderation(bot))
