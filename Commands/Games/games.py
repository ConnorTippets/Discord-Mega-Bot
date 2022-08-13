import discord
from discord.ext import commands
import random
import asyncio
import copy
import upsidedown
from discord.ext import ui
from discord.utils import get
import time
from discord.ext import menus
import io
from akinator.async_aki import Akinator
import akinator
from random_word import RandomWords

eightBall_msgs = ["It is certain","Without a doubt", "\
You may rely on it","\
Yes definitely","\
It is decidedly so","\
As I see it, yes","\
Most likely","\
Yes","\
Outlook good","\
Signs point to yes","\
Reply hazy try again","\
Better not tell you now","\
Ask again later","\
Cannot predict now","\
Concentrate and ask again","\
Don’t count on it","\
Outlook not so good","\
My sources say no","\
Very doubtful","\
My reply is no"]
    
rocpapscie = {'scissors':':scissors:', 'paper':':page_facing_up:', 'rock':':rock:'}
rpsrules = {'rock': 'scissors', 'paper': 'rock', 'scissors': 'paper'}
rocpapsci = ['scissors', 'paper', 'rock']

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.wtp_is_playing = False
        self.aki = Akinator()
        self.ttt_canvas = ['⬜', '⬜', '⬜', '⬜', '⬜', '⬜', '⬜', '⬜', '⬜']
        self.current_player_ttt = [None, None]
        self.current_players_ttt = [[None, None], [None, None]]
        self.ttt_ended = False
    
    def parse_input_ttt(self, i):
        if i == "\N{CROSS MARK}":
            return False
        else:
            return True
    
    def generate_response_ttt(self):
        resp = ''
        for place in range(len(self.ttt_canvas)):
            if place in (2, 5):
                resp += (self.ttt_canvas[place] + '\n')
                continue   
            resp += self.ttt_canvas[place]
        return resp
    
    def generate_canvas_from_response_ttt(self, resp):
        return list(resp.replace("\n", ""))
    
    def do_place_ttt(self, place):
        self.ttt_canvas[place-1] = self.current_player_ttt[1]
    
    def reset_canvas_ttt(self):
        self.ttt_canvas = ['⬜', '⬜', '⬜', '⬜', '⬜', '⬜', '⬜', '⬜', '⬜']
    
    def winning_detection_ttt(self):
        if any(['❌']*3 == [self.ttt_canvas[0+_], self.ttt_canvas[3+_], self.ttt_canvas[6+_]] for _ in range(3)) or any(['⭕']*3 == [self.ttt_canvas[0+_], self.ttt_canvas[3+_], self.ttt_canvas[6+_]] for _ in range(3)):
            return (True, self.current_player_ttt[0])
        elif any(['❌']*3 == [self.ttt_canvas[0+_], self.ttt_canvas[1+_], self.ttt_canvas[2+_]] for _ in [0, 3, 6]) or any(['⭕']*3 == [self.ttt_canvas[0+_], self.ttt_canvas[1+_], self.ttt_canvas[2+_]] for _ in [0, 3, 6]):
            return (True, self.current_player_ttt[0])
        elif [self.ttt_canvas[0], self.ttt_canvas[4], self.ttt_canvas[8]] in [['❌', '❌', '❌'], ['⭕', '⭕', '⭕']] or [self.ttt_canvas[2], self.ttt_canvas[4], self.ttt_canvas[6]] in [['❌', '❌', '❌'], ['⭕', '⭕', '⭕']]:
            return (True, self.current_player_ttt[0])
        return (False)
    
    @commands.command(brief='A classic game of rock paper scissors')
    async def rps(self, ctx, ropasc):
        embed = discord.Embed(color=0x2F3136, title="Rock Paper Scissors")
        if not ropasc in rocpapsci:
            embed.title = "Invalid Argument"
            embed.description = "Valid Choices: Rock, Paper, and Scissors"
            await ctx.send(embed=embed)
            return
        a = random.choice([a for a in rocpapscie])
        if ropasc in rpsrules[a]:
            embed.title = "I win!"
        else:
            embed.title = "You win!"
        embed.description = '{} vs {}'.format(rocpapscie[a], rocpapscie[ropasc])
        await ctx.send(embed=embed)
    
    @commands.command(name='8ball', brief='Shows you a random answer to your yes or no question')
    async def _8ball(self, ctx, *, question):
        embed = discord.Embed(color=0x2F3136, title=question)
        answer = random.choice(eightBall_msgs)
        embed.description = answer+"."
        await ctx.send(embed=embed)
    
    @commands.command(brief='Makes the bot roll a dice for you')
    async def roll(self, ctx, dice:int=3):
        if dice > 20:
            await ctx.send(f'Sorry, but i don\'t have {dice} dice')
            return
        if dice < 1:
            await ctx.send(f'Sorry, but i don\'t have {dice} die')
            return
        a = []
        for x in range(dice):
            a.append(str(random.randint(0, 10)))
        await ctx.send('You Rolled: \n`' + (', '.join(a)) + '`')
    
    @commands.command(brief='Makes the bot choose a random option out of what you give it')
    async def choose(self, ctx, *args):
        choice = random.choice(args)
        await ctx.send(choice)
    
    @commands.command(brief='Spins a fidget spinner')
    async def spinner(self, ctx):
        a = random.randint(1, 50)
        if random.randint(1, 2) == 1:
            a = random.randint(1, 25)
        embed = discord.Embed(color=0x2F3136, title="Fidget Spinner")
        embed.description = 'You started spinning a fidget spinner, lets see how long it spins!'
        msg = await ctx.send(embed=embed)
        await asyncio.sleep(1)
        embed.description = 'Currently spinning...'
        await msg.edit(embed=embed)
        await asyncio.sleep(a)
        embed.description = ""
        embed.add_field(name="Total Seconds Spun:", value=str(a), inline=False)
        await msg.edit(embed=embed)
    
    @commands.command(brief='Generates a random number and makes you guess it')
    async def guessnum(self, ctx, guess:int):
        num = random.randint(1, 10)
        if guess is num:
            await ctx.send('Correct!')
        else:
            await ctx.send(f'Too bad, you got it wrong! I was thinking of {num}.')
    
    @commands.command(brief='Roasts people, roasty toasty!')
    async def roast(self, ctx, member:discord.Member = None):
        await ctx.send(f'**{ctx.author.name if not member else member.name}**, {await self.bot.dag.roast()}')
    
    @commands.command(brief='Catch the pie within the time')
    async def pie(self, ctx):
        embed = discord.Embed(title='Catch the Pie!', color=0x2F3136, description='3')
        msg = await ctx.send(embed=embed)
        for x in ['2', '1']:
            await asyncio.sleep(1)
            embed.description = x
            await msg.edit(embed=embed)
        await asyncio.sleep(1)
        embed.description = 'NOW'
        await msg.edit(embed=embed)
        await msg.add_reaction('\U0001f967')
        time_perf = time.perf_counter()
        def check(reaction, user):
            return str(reaction.emoji) == '🥧' and user.name != self.bot.user.name
        
        reaction, user = await self.bot.wait_for('reaction_add', check=check)
        embed.description = user.name + ' got it in ' + str(round((time.perf_counter()-time_perf) * 1000, 6)) + 'ms'
        await msg.edit(embed=embed)
    
    @commands.command(brief='Shows a picture of a cat with an http status code')
    async def http(self, ctx, status_code:int):
        async with self.bot.session.get(f'https://http.cat/{status_code}') as resp:
            data = io.BytesIO(await resp.read())
            await ctx.send(file=discord.File(data, 'cool_image.png'))
    
    @commands.command(brief='Roo.')
    async def roo(self, ctx):
        emojis = [emoji for emoji in self.bot.emojis if emoji.name.startswith('roo')]
        emoji = random.choice(emojis)
        await ctx.send(emoji)
    
    @commands.command(brief='Ship two people together')
    async def ship(self, ctx, mem1:discord.Member, mem2:discord.Member):
        bar = await self.bot.utils.moving_bar()
        embed = discord.Embed(title='Shipping', description=f'Calculating love...\n{bar[0]}', color=0x2F3136)
        msg = await ctx.send(embed=embed)
        for i in range(1, len(bar)):
            await asyncio.sleep(1)
            embed.description = f'Calculating love...\n{bar[i]}'
            await msg.edit(embed=embed)
        embed.description = f'Calculated love:\n{random.randint(0, 100)}'
        await msg.edit(embed=embed)
    
    @commands.command(brief='Starts a game of akinator')
    async def akinator(self, ctx):
        check = lambda msg: msg.channel.id == ctx.channel.id and msg.author.id == ctx.author.id
        q = await self.aki.start_game()
        index = 1
        last_answer = None
        embed = discord.Embed(title='Akinator', description=f'Question #{index}\n**placeholder**\nType cancel to end.')
        while self.aki.progression <= 80:
            embed.description = f'Question #{index}\n**'+self.aki.question+'**\nType cancel to end.'
            if not last_answer:
                m = await ctx.send(embed=embed)
            else:
                m = await last_answer.reply(embed=embed, mention_author=False)
            a = await self.bot.wait_for('message', check=check)
            await m.delete()
            last_answer = a
            if a.content.lower() in ("back", "b"):
                try:
                    q = await self.aki.back()
                    index-=1
                except akinator.CantGoBackAnyFurther:
                    pass
            if a.content.lower() in ("end", "cancel", "last"):
                return
            else:
                try:
                    q = await self.aki.answer(a.content)
                except akinator.InvalidAnswerError:
                    pass
                index+=1
        await self.aki.win()
        m = await ctx.send(f"It's {self.aki.first_guess['name']} ({self.aki.first_guess['description']})! Was I correct?\n{self.aki.first_guess['absolute_picture_path']}\n\t")
        l = await self.bot.wait_for('message', check=check)
        if l.content.lower() in ("yes", "ye", "y"):
            await ctx.send('Yay!')
        if l.content.lower() in ("no", "not", "n"):
            await ctx.send("Aw man :(")
    
    @commands.group(brief='A game of TicTacToe', invoke_without_command=True)
    async def ttt(self, ctx, *, member:discord.Member=None):
        if not member:
            return await ctx.send('Please mention one person to play with')
        if hasattr(self, 'game_msg'):
            return await ctx.send("There is already a game currently playing!")
        self.reset_canvas_ttt()
        approval = False
        try:
            if not member == self.bot.user:
                approvalmsg = await ctx.send(f'{member.mention}, {ctx.author.name} has challenged you to a game of tictactoe, do you accept?')
                for emoji in ("\N{CROSS MARK}", "\N{WHITE HEAVY CHECK MARK}"):
                    await approvalmsg.add_reaction(emoji)
                r, u = await self.bot.wait_for("reaction_add", timeout=60, check=lambda r, u: r.emoji in ("\N{CROSS MARK}", "\N{WHITE HEAVY CHECK MARK}") and r.message.id == approvalmsg.id and u.id == member.id)
                i = self.parse_input_ttt(r.emoji)
                if i == True:
                    approval = True
                else:
                    approval = False
            else:
                await ctx.send("A game with me, eh?\nI appreciate the thought, but I can't play TicTacToe.")
                return
        except asyncio.TimeoutError:
            approval = False
            await ctx.send(f"{ctx.author.mention}, {member.name} didn't respond in time")
        if approval:
            self.current_players_ttt = [[ctx.author, '❌'], [member, '⭕']]
            self.current_player_ttt = random.choice(self.current_players_ttt)
            self.game_msg = await ctx.send(self.generate_response_ttt() + f"\n\n {self.current_players_ttt[0][0].name}: {self.current_players_ttt[0][1]}\n{self.current_players_ttt[1][0].name}: {self.current_players_ttt[1][1]}\n\nCurrent Player: {self.current_player_ttt[0].name}")
        else:
            return
        while not self.ttt_ended:
            if not hasattr(self, 'game_msg'):
                return
            try:
                m = await self.bot.wait_for("message", check=lambda m: m.author.id == self.current_player_ttt[0].id and m.content in [*"123456789", "stop", "cancel", "end"] and not m.author.id == self.bot.user.id)
                if m.content.isdigit():
                    await self.bot.get_command('ttt place')(await self.bot.get_context(m), int(m.content))
                elif m.content.lower() in ("stop", "cancel", "end"):
                    await self.bot.get_command('ttt stop')(await self.bot.get_context(m))
                    return
            except AttributeError or ValueError:
                return
    
    @ttt.command()
    async def place(self, ctx, place:int):
        if not hasattr(self, 'game_msg'):
            return await ctx.send('There isn\'t a game of tictactoe currently playing!')
        if not self.current_player_ttt[0].id == ctx.author.id:
            return await ctx.send('It\'s not your turn!')
        if self.ttt_canvas[place-1] in ('❌', '⭕'):
            return await ctx.send('This spot is occupied.')
        self.do_place_ttt(place)
        try:
            self.current_player_ttt = self.current_players_ttt[self.current_players_ttt.index(self.current_player_ttt)+1]
        except:
            self.current_player_ttt = self.current_players_ttt[self.current_players_ttt.index(self.current_player_ttt)-1]
        winner = self.winning_detection_ttt()
        await self.game_msg.edit(content=self.generate_response_ttt() + f"\n\n {self.current_players_ttt[0][0].name}: {self.current_players_ttt[0][1]}\n{self.current_players_ttt[1][0].name}: {self.current_players_ttt[1][1]}\n\nCurrent Player: {self.current_player_ttt[0].name}")
        try:
            if winner[0]:
                await self.game_msg.edit(content=self.game_msg.content + f"\n\n{winner[1].name} won!")
                self.current_player_ttt = [None, None]
                self.current_players_ttt = [[None, None], [None, None]]
                delattr(self, 'game_msg')
                self.ttt_ended = True
                return await ctx.send(f'{winner[1].mention} You won!')
        except TypeError:
            return
    
    @ttt.command()
    async def stop(self, ctx):
        if not hasattr(self, 'game_msg'):
            return await ctx.send('There isn\'t a game of tictactoe currently playing!')
        self.current_player_ttt = [None, None]
        self.current_players_ttt = [[None, None], [None, None]]
        delattr(self, 'game_msg')
        return await ctx.send("Stopped.")

async def async_setup(bot):
  await bot.add_cog(Games(bot))

def setup(bot):
  return async_setup(bot)
  bot.add_cog(Games(bot))
