from pathlib import Path
import os

os.chdir("C:/Users/Nanny/Documents/Discord Bot/The Former/Discord Mega Bot/DiscordMegaBot")
bp = os.getcwd()
os.chdir(bp + "/Commands/")
path = Path('.')
subdirs = []
for x in path.iterdir():
    print(x)
    if x.is_dir() and not str(x) == "__pycache__":
        print(str(x) + " is a dir")
        subdirs.append(x)
cogs = []
cogsidx = 0
for dis in subdirs:
    cogs.append([])
    cogs[cogsidx].append(str(dis))
    constructed_path = f'Commands.{cogs[cogsidx][0]}.{cogs[cogsidx][0].lower()}'
    cogs[cogsidx] = constructed_path
    cogsidx = cogsidx + 1
os.chdir(bp)
