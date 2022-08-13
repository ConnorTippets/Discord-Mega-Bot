import random
import humanize
import asyncio

class Bingo:
    def __init__(self, bot, author, channel):
        self.bot = bot
        self.author = author
        self.channel = channel
        self.gen_board()
        self.current_column = (None, None)
    
    def index_from_num(self, num):
        found = []
        for i, lst in enumerate(self.board):
            column_num = lst[self.current_column[1]]
            if column_num == num:
                found.append((i, self.current_column[1]))
        return found if found else None
    
    def gen_board(self):
        ret = [[], [], [], [], []]
        for k in range(5):
            for v in range(5):
                ret[k].append(random.randint(0, 10) if not (k == 2 and v == 2) else 'Free')
        self.board = ret
    
    def number_to_emoji(self, num):
        return (f':{humanize.apnumber(num)}:' if not num == 10 else ':keycap_ten:') if not type(num) == str else ':green_circle:'
    
    def pretty_board(self):
        nums = ' ' + ' \n '.join([' '.join([self.number_to_emoji(a) for a in e]) for e in self.board])
        return f'\nB     I      N      G      O\n\n{nums}\n'
    
    def generate_column(self):
        column = random.choice(['B', 'I', 'N', 'G', 'O'])
        if column == 'B':
            index = 0
        elif column == 'I':
            index = 1
        elif column == 'N':
            index = 2
        elif column == 'G':
            index = 3
        else:
            index = 4
        self.current_column = (column, index)
        num = random.randint(0, 10)
        return num
    
    def winning_detection(self):
        if any(all(x == ':green_circle:' for x in lst) for lst in self.board):
            return True
        elif any(all(lst[i] == ':green_circle:' for lst in self.board) for i in range(len(self.board))):
            return True
        elif self.board[0][0] == ':green_circle:' and self.board[1][1] == ':green_circle:' and self.board[2][2] == ':green_circle:' and self.board[3][3] == ':green_circle:' and self.board[4][4] == ':green_circle:':
            return True
        elif self.board[0][4] == ':green_circle:' and self.board[1][3] == ':green_circle:' and self.board[2][2] == ':green_circle:' and self.board[3][1] == ':green_circle:' and self.board[4][1] == ':green_circle:':
            return True
        return False
    
    async def main(self):
        await self.channel.send('Get ready for a game of Bingo!')
        await asyncio.sleep(2)
        _origin = self.pretty_board()
        hasWon = False
        game_msg = await self.channel.send(_origin)
        for i, e in enumerate([1, 1, 1]):
            await asyncio.sleep(1)
            if i == 0:
                await game_msg.edit(content=_origin +'\n\nStarting in 3 seconds...')
            elif i == 1:
                await game_msg.edit(content=_origin +'\n\nStarting in 2 seconds...')
            elif i == 2:
                await game_msg.edit(content=_origin +'\n\nStarting in 1 seconds...')
        while not hasWon:
            n = self.generate_column()
            await game_msg.edit(content=_origin + f'\n\nStarted! Chosen number: {self.current_column[0]}:{n}')
            move = await self.bot.wait_for('message', check=lambda x: (x.content.startswith('use ') or x.content.startswith('bingo')) and x.author.id == self.author.id and x.channel.id == self.channel.id)
            if move.content == 'bingo':
                _hasWon = self.winning_detection()
                if _hasWon:
                    print('Has Won.')
                    await game_msg.edit(content=_origin + f'\n\nCongratulations! You just won!')
                    hasWon = True
                else:
                    print('Hasn\'t Won.')
                    continue
            elif move.content == 'continue':
                await asyncio.sleep(0)
            elif move.content.startswith('use'):
                used = self.index_from_num(int(move.content.removeprefix('use ').split(':')[1]))
                if used is None:
                    continue
                else:
                    for r, n in used:
                        self.board[r][n] = 'Used'
                    _origin = self.pretty_board()
            elif move.content.startswith('cancel'):
                await game_msg.edit(content=_origin + f'\n\nGame Ended.')
                return
