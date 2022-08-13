games = []

class Userphone:
    def __init__(self):
        self.self = self
        self.channels = []
        self.is_open = True
    
    async def create(self, ctx):
        if self.self.is_open == False:
            return await ctx.send('There is already a conversation active')
        games.append(self.self)
        self.self.channels.append(ctx.channel)
        await ctx.send('Open conversation opened! Please wait for a user to connect')
    
    async def connect(self, ctx):
        try:
            conv = games[-1]
        except:
            return await self.create(ctx)
        self.self = conv
        self.self.channels.append(ctx.channel)
        games.remove(self.self)
        self.self.is_open = False
        await self.self.channels[1].send('Connection established.')
        await self.self.channels[0].send('Other party connected.')
    
    async def send(self, ctx):
        if ctx.channel.id == self.self.channels[0].id:
            if ctx.attachments:
                if len(ctx.attachments) > 1:
                    files = [att.to_file() for att in ctx.attachments]
                    await self.self.channels[1].send(f'{str(ctx.author)}: {ctx.content}', files=files)
                else:
                    files = ctx.attachments[0].to_file()
                    await self.self.channels[1].send(f'{str(ctx.author)}: {ctx.content}', file=files)
            else:
                await self.self.channels[1].send(f'{str(ctx.author)}: {ctx.content}')
        else:
            if ctx.attachments:
                if len(ctx.attachments) > 1:
                    files = [att.to_file() for att in ctx.attachments]
                    await self.self.channels[0].send(f'{str(ctx.author)}: {ctx.content}', files=files)
                else:
                    files = ctx.attachments[0].to_file()
                    await self.self.channels[0].send(f'{str(ctx.author)}: {ctx.content}', file=files)
            else:
                await self.self.channels[0].send(f'{str(ctx.author)}: {ctx.content}')
    
    async def close(self, ctx):
        index = self.self.channels.index(ctx.channel)
        if index == 1:
            await self.self.channels[0].send('The other party disconnected')
            await self.self.channels[1].send('You hung up the userphone')
        else:
            await self.self.channels[1].send('The other party disconnected')
            await self.self.channels[0].send('You hung up the userphone')
        self.self.is_open = True
    
    async def main(self, ctx):
        if self.self.is_open:
            await self.connect(ctx)
        else:
            return await self.create(ctx)
        while not self.self.is_open:
            msg = await ctx.bot.wait_for('message', check=lambda x: x.channel in self.self.channels and not x.author.bot)
            if not msg.content == ctx.prefix + 'hangup':
                try:
                    await self.send(msg)
                except:
                    continue
            else:
                await self.close(ctx)
