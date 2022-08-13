class AlreadyInDB(Exception):
    pass

class FakeFile:
    def __init__(self, bot, name, contents):
        self.bot = bot
        self.name = name
        self.code = contents
        self._actual = self
    
    @property
    def actual(self):
        return self._actual
    
    @actual.setter
    def set_x(self, new):
        self._actual = new

class FakeFiles:
    def __init__(self, bot):
        self.bot = bot
        self.current = None
    
    async def set(self, content):
        self.current.code = content
    
    async def setcurrent(self, name):
        if not name in [c[0] for c in self.bot.db.execute('SELECT name FROM fakefiles').fetchall()]:
            raise NameError(f'Unknown fake file: "{name}"')
        else:
            code = self.bot.db.execute('SELECT code FROM fakefiles WHERE name = ?', (name,)).fetchall()[0][0]
            self.current = FakeFile(self.bot, name, code).actual
    
    async def add(self, appender):
        self.current.code += appender
    
    async def new_file(self, name, code):
        if name in [c[0] for c in self.bot.db.execute('SELECT name FROM fakefiles').fetchall()]:
            raise AlreadyInDb(f'Fake file "{name}" already exists')
        else:
            self.bot.db.execute('INSERT INTO fakefiles(name, code) VALUES (?, ?)', (name,code,))
            self.bot._conn.commit()
            self.current = FakeFile(self.bot, name, code).actual
    
    async def rem(self, remover):
        self.current.code = self.current.code.replace(remover, '')
    
    async def delete(self, name):
        if not name in [c[0] for c in self.bot.db.execute('SELECT name FROM fakefiles').fetchall()]:
            raise NameError(f'Unknown fake file: "{name}"')
        else:
            self.bot.db.execute('DELETE FROM fakefiles WHERE name = ?', (name,))
            self.bot._conn.commit()
    
    async def get_file(self, name):
        if not name in [c[0] for c in self.bot.db.execute('SELECT name FROM fakefiles').fetchall()]:
            raise NameError(f'Unknown fake file: "{name}"')
        else:
            code = self.bot.db.execute('SELECT code FROM fakefiles WHERE name = ?', (name,)).fetchall()[0][0]
            self.current = FakeFile(self.bot, name, code).actual
            return self.curreny
