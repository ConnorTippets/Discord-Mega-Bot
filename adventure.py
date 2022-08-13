class Adventure:
    def __init__(self, bot, author, channel):
        self.bot = bot
        self.direction = None
        self.starter = author
        self.channel = channel
        self.traversed_locations = []
        self.location_index = 0
        self.location_index_index = 0
        self.locations = [
            ('treehouse', 'cave'),
            ('chest', 'crystal'),
            ('gold')
            ]
        self.location = self.locations[self.location_index][self.location_index_index]
    
    def normal_check(self, message):
        return message.content.lower() in [self.locations[self.location_index][0], self.locations[self.location_index][1] if self.locations[self.location_index][1] else None, 'leave'] and message.author.id == self.starter.id and message.channel.id == self.channel.id
    
    async def wait_for(self):
        m = await self.bot.wait_for('message', check=self.normal_check)
        self.location_index+=1
        if m.content.lower() != 'leave':
            self.traversed_locations.append(m.content.lower())
        else:
            try:
                self.traversed_locations.pop(-1)
            except IndexError:
                pass
        return m
    
    async def treehouse(self):
        await self.channel.send('You found your way into the treehouse, in there you find a chest... go to the chest, or leave? (chest/leave)')
        response = await self.wait_for()
        if response.content.lower() == 'chest':
            await self.channel.send('You go to the chest, and find gold in it! What a delight. This is the end of your adventure.')
            return response
        if response.content.lower() == 'leave':
            await self.main()
        return response
    
    async def cave(self):
        await self.channel.send('You are in a cave, and you find a magical crystal... touch it, or leave? (crystal/leave)')
        response = await self.wait_for()
        if response.content.lower() == 'crystal':
            await self.channel.send('The crystal uses its magical powers to disintegrate you! Well, i guess thats the end.')
            return response
        if response.content.lower() == 'leave':
            await self.main()
        return response
    
    async def main(self):
        await self.channel.send('You are standing in the middle of a forest, you have a cave and treehouse in front of you, which one do you pick? (cave/treehouse)')
        response = await self.wait_for()
        if response.content.lower() == 'treehouse':
            response = await self.treehouse()
        if response.content.lower() == 'cave':
            response = await self.cave()
        if response.content.lower() == 'leave':
            await self.channel.send('I\'m sorry, but you can\'t leave!')
            await self.main()
    
    async def start(self):
        await self.main()
