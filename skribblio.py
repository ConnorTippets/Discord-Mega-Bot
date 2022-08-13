import secrets
import discord
import random_word

class SkribblioGame:
    def __init__(self, options: dict, host: discord.User):
        self.options = options
        self.players = 1
        self.host = host
        self.id = secrets.token_urlsafe(12)
        self.guessers = []
        self.words = options['custom_words'] or random_words.RandomWords().get_random_words(limit=options['rounds']*2, hasDictionaryDef="true")

games = []

class Skribblio:
    def __init__(self, bot):
        self.bot = bot
        self.self = self
    async def create(self, options: dict, host: discord.User):
        game = SkribblioGame(options, host)
        games.append(game)
        await host.send('Game created, use the id {} to invite other people'.format(game.id))
        game.player_msg = await host.send('1 Person, Can\'t play.')
        self.self = game
    
    async def find(self, id: str):
        for game in games:
            if game.id = id:
                return game
        return None
    
    async def join(self, author: discord.User, id: str):
        game = await self.find(id)
        self.self = game
        self.self.guessers.append(author)
        self.self.players += 1
        await self.self.player_msg.edit(content='1 Person, Can\'t play.' if self.self.players == 1 else '{} People, Do you want to start?'.format(self.self.players))
    
    async def start(self, author: discord.User):
        if self.self = self:
            return await author.send('No game to start!')
        elif self.self.host != author:
            return await author.send('You don\'t own this game!')
        elif self.self.players == 1:
            return await author.send('Only 1 Player.')
        roundn = 0
        while roundn < self.self.options['rounds']:
            await self.self.host.send('Starting...')
            words = self.self.words[::2]
            drawer = random.choice(self.self.guessers)
            await drawer.send("You have been selected as the drawer for this round, please send an image of the word {}".format(words[roundn]))
            m = await self.bot.wait_for('message', check=lambda x: x.author == drawer and x.channel == drawer.dm_channel)
