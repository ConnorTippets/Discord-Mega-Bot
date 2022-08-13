class Tag:
    def __init__(self, callback, name):
        self.tags = {}
        self.callback = callback
        self.name = name
    
    def tag(self, name):
        def wrapper(func):
            self.tags[name] = func
            return func()
        return wrapper

class Parser:
    def __init__(self):
        self.tags = {}
    
    def tag(self, name):
        def wrapper(func):
            returner = Tag(func, name)
            self.tags[name] = returner
            return returner
        return wrapper
    
    def parse(self, string):
        for name, func in self.tags.items():
            string = string.replace(f'{{{name}}}', func.callback())
            if func.tags:
                for name, subfunc in func.tags.items():
                    string = string.replace(f'{{{func.name}.{name}}}', subfunc.callback())
        return string
