import os

class ConLan:
    def __init__(self, bot):
        self.bot = bot
        self.var_dict = {}
        self.file_dict = {}
        for f in os.listdir('.'):
            if not f.startswith('.'):
                try:
                    file = open(f, 'r')
                    self.file_dict[f] = file.read()
                    file.close()
                except (UnicodeDecodeError, PermissionError):
                    continue
    
    async def run(self, code):
        output = []
        if code.__class__.__name__ == 'list':
            pass
        else:
            code = code.split('\n')
            for x in range(len(code)):
                if code[x].startswith('var'):
                    format = code[x][4:]
                    name, content = format.split(':')
                    if content.startswith('"'):
                        self.var_dict[name] = content.replace('"', '')
                    elif content.startswith('%'):
                        try:
                            self.var_dict[name] = self.var_dict[content.replace('%', '')]
                        except KeyError:
                            var = content.rstrip('"')
                            return f"NameError: \"{var}\" does not exist"
                    else:
                        return f'NameError: Unknown Name "{content.split()[0]}"'
                elif code[x].startswith('echo'):
                    if code[x][5:].startswith('%'):
                        try:
                            output.append(self.var_dict[code[x][5:].split('%')[1]])
                        except KeyError:
                            return f'NameError: "{code[x][5:].split("%")[1]}" does not exist'
                    else:
                        if code[x][5:].startswith('"'):
                            if code[x][5:].endswith('"'):
                                output.append(code[x].removeprefix('echo "').removesuffix('"'))
                            else:
                                return "SyntaxError: '\"' not matched"
                        else:
                            return f'NameError: Unknown Name "{code[x][5:].split()[0]}"'
                elif code[x].startswith('newline'):
                    output.append('\n')
                elif code[x].startswith('eval'):
                    expr = code[x][5:]
                    if expr.startswith('"'):
                        output.append(await self.run(expr.removesuffix('"').removeprefix('"')))
                    elif expr.startswith("%"):
                        try:
                            output.append(await self.run(self.var_dict[expr.replace("%", "")]))
                        except KeyError:
                            return f'NameError: "{expr.replace("%", "")}" does not exist'
                elif code[x].startswith('import'):
                    mod = code[x][7:]
                    if mod+'.cli' in os.listdir('.'):
                        file = self.file_dict[mod+'.cli']
                        recur = ConLan(self.bot)
                        recur_out = await recur.run(file)
                        output.append(recur_out)
                        self.var_dict.update(recur.var_dict)
                    else:
                        return f'ImportError: No module named "{mod}"'
                else:
                    return f'NameError: Unknown Name "{code[x].split()[0]}"'
        return '\n'.join(output)
