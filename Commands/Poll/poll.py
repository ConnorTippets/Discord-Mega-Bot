import discord
from discord.ext import commands
import asyncio
import random

class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.polls = {}
    
    @commands.group(brief='Manages polls')
    async def poll(self, ctx):
        pass
    
    @poll.command(brief='Creates a poll')
    async def create(self, ctx, question, *answers):
        if len(answers) > 20:
            return await ctx.send('Too many options!')
        a = ''
        emojis = []
        for i in range(len(answers)):
            emoji = f':regional_indicator_{chr(ord("a") + i)}:'
            reaction_emoji = chr(127462 + i)
            name = answers[i]
            emojis.append((emoji, reaction_emoji, name))
            a += f'{emoji}. {answers[i]}\n'
        embed = discord.Embed(title='Poll', color=0x2F3136, description=f'**{question}**\n{a}')
        embed.set_footer(text=f'Poll ID: {len(self.polls)+1}')
        msg = await ctx.send(embed=embed)
        for emoji in emojis:
            await msg.add_reaction(emoji[1])
        self.polls[len(self.polls)+1] = msg
    
    @poll.command(brief='Deletes a poll')
    async def delete(self, ctx, id:int):
        msg = self.polls.get(id-1)
        if not msg:
            return await ctx.send('Unknown message.')
        if msg.author.id != ctx.author.id:
            return await ctx.send('Improper permissions to delete poll.')
        await msg.delete()
        del self.polls[id]
        await ctx.send('Deleted.')

async def async_setup(bot):
  await bot.add_cog(Poll(bot))

def setup(bot):
  return async_setup(bot)
  bot.add_cog(Poll(bot))
