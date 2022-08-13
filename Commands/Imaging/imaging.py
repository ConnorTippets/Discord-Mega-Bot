import io, json, asyncio, aiohttp, math
from PIL import Image, ImageDraw, ImageFilter, ImageColor, ImageSequence, ImageFont, ImageOps
import discord
from discord.ext import commands
from os import getcwd
import numpy as np
from wand.image import Image as wImage

image_dir = getcwd() + '/Commands/Imaging/'
blocks = {
        '-': (0,0,0),
        '1': (0,0,0),
        '2': (255,0,0),
        '3': (255,165,0),
        '4': (255,255,0),
        '5': (0,255,0),
        '6': (0,0,255),
        '7': (255,255,255)
    }

def wand_gif(frames, durations):
	"""A function to render pil frames with transparency support
	frames: list of pil images
	durations: int or list of ints to set duration of each frame in ms
	-> io.BytesIO
	"""
	if isinstance(durations, int):
		durations = [durations] * len(frames)

	durations = np.array(durations) // 10

	with wImage.from_array(np.array(frames[0])) as bg:
		for i, pframe in enumerate(frames):
			with wImage.from_array(np.array(pframe.convert('RGBA'))) as frame:
				frame.dispose = 'background'
				bg.composite(frame, 0, 0)
				frame.delay = durations[i]
				bg.sequence.append(frame)
		bg.sequence.pop(0)
		bg.dispose = 'background'
		bg.format = 'gif'
		buf = io.BytesIO()
		bg.save(file=buf)
		buf.seek(0)
	return buf

def color_to_rgb(color, default):
    try:
        return ImageColor.getrgb(color)
    except:
        return ImageColor.getrgb(default)

def of(elem, list, default):
    try:
        return list[elem]
    except:
        return default[elem]

def get_coor(coor, default):
    outliers = []
    for x, y in coor:
        if type(x) != int:
            outliers.append(x)
        elif type(y) != int:
            outliers.append(y)
    if outliers:
        return [(of(0, outliers, coor[0]), of(1, outliers, coor[0])), (of(2, outliers, coor[0]), of(3, outliers, coor[0]))]
    return coor

async def rectangle(x1, y1, x2, y2, color, image_url=None):
    im = None
    if image_url:
        async with aiohttp.ClientSession() as cs:
            async with cs.get(image_url) as r:
                image = io.BytesIO(await r.read())
        im = Image.open(image).resize((600, 400), 2)
    else:
        im = Image.new('RGB', (600, 400))
    draw = ImageDraw.Draw(im)
    draw.rectangle(get_coor([(x1, y1), (x2, y2)], 0), fill=color_to_rgb(color, 'green'))
    i = io.BytesIO()
    im.save(i, 'PNG')
    i.seek(0)
    return i

async def ellipse(x1, y1, x2, y2, color, image_url=None):
    im = None
    if image_url:
        async with aiohttp.ClientSession() as cs:
            async with cs.get(image_url) as r:
                image = io.BytesIO(await r.read())
        im = Image.open(image).resize((600, 400), 2)
    else:
        im = Image.new('RGB', (600, 400))
    draw = ImageDraw.Draw(im)
    draw.ellipse(get_coor([(x1, y1), (x2, y2)], 0), fill=color_to_rgb(color, 'green'))
    i = io.BytesIO()
    im.save(i, 'PNG')
    i.seek(0)
    return i

async def emboss(avatar_url):
    async with aiohttp.ClientSession() as cs:
        async with cs.get(avatar_url) as r:
            avatar = await r.read()
    with Image.open(io.BytesIO(avatar)) as im:
        im1 = im.filter(ImageFilter.EMBOSS)
        i = io.BytesIO()
        im1.save(i, 'PNG')
        i.seek(0)
    return i

async def blur(avatar_url):
    async with aiohttp.ClientSession() as cs:
        async with cs.get(avatar_url) as r:
            avatar = await r.read()
    with Image.open(io.BytesIO(avatar)) as im:
        im1 = im.filter(ImageFilter.BLUR)
        i = io.BytesIO()
        im1.save(i, 'PNG')
        i.seek(0)
    return i

async def wawa(text):
    im1 = Image.open(image_dir+'wawa-cat.gif')
    frames = []
    flippedframes = []
    for frame in ImageSequence.Iterator(im1):
        frame = frame.resize((300, 300), 2)
        frame2 = ImageOps.mirror(frame.copy())
        with Image.new('RGBA', (frame.width, round(frame.height+frame.height/3)), (255,255,255,255)) as im2:
            im2.paste(frame, (0, round(frame.height/3)))
            d = ImageDraw.Draw(im2)
            font = ImageFont.truetype(image_dir+"Roboto-Bold.ttf", 35)
            d.text((6,6), text, fill=(0,0,0,255), font=font)
            del d
            frames.append(im2)
        with Image.new('RGBA', (frame.width, round(frame.height+frame.height/3)), (255,255,255,255)) as im3:
            im3.paste(frame2, (0, round(frame.height/3)))
            d = ImageDraw.Draw(im3)
            font = ImageFont.truetype(image_dir+"Roboto-Bold.ttf", 35)
            d.text((6,6), text, fill=(0,0,0,255), font=font)
            del d
            flippedframes.append(im3)
    frames = frames + flippedframes
    i = io.BytesIO()
    frames[0].save(i, format='GIF', save_all=True, append_images=frames[1:], loop=0)
    i.seek(0)
    return i

async def isod2d(input_raw, gif=False, from_iti=False):
    tile_size = 16
    mapping = {'0':'', '1':'black', '2':'red', '3':'orange', '4':'yellow', '5':'green', '6':'blue', '7':'white'}
    input = input_raw.replace('-', '\n').split('\n')
    width = len(max(input, key=len))*tile_size
    height = (input_raw.count('\n')+1)*tile_size
    input_bc = input_raw
    for xy in input_bc:
        if not xy in blocks:
            input_bc = input_bc.replace(xy, '')
    block_count = len(input_bc)
    if block_count > 750 and not gif and not from_iti:
        return io.BytesIO()
    if block_count > 350 and gif:
        return io.BytesIO()
    if (width/tile_size*height/tile_size)>550 and not from_iti:
        return io.BytesIO()
    if not gif:
        with Image.new('RGBA', (width, height), (0,0,0,0)) as im1:
            current_x = 0
            current_y = 0
            for y in input:
                for x in y:
                    try:
                        image = image_dir+mapping[x]+'.png'
                        if image == image_dir+'.png':
                            dont_open = True
                        else:
                            dont_open = False
                        if not dont_open:
                            im2 = Image.open(image).resize((tile_size,tile_size), 2)
                            im1.paste(im2, (current_x, current_y))
                        outer_inc = True
                    except KeyError:
                        outer_inc = False
                        current_x += tile_size
                    if outer_inc:
                        current_x += tile_size
                current_y += tile_size
                current_x = 0
            i = io.BytesIO()
            im1 = im1.resize((im1.width*2, im1.height*2), 2)
            im1.save(i, format='PNG')
            i.seek(0)
        return i
    else:
        frames = []
        with Image.new('RGBA', (width, height), (0,0,0,0)) as im1:
            current_x = 0
            current_y = 0
            for y in input:
                for x in y:
                    im1 = im1.copy()
                    try:
                        image = image_dir+mapping[x]+'.png'
                        if image == image_dir+'.png':
                            dont_open = True
                        else:
                            dont_open = False
                        if not dont_open:
                            im2 = Image.open(image).resize((tile_size,tile_size), 2)
                            im1.paste(im2, (current_x, current_y))
                            frames.append(im1.resize((im1.width*2, im1.height*2), 2))
                        outer_inc = True
                    except KeyError:
                        outer_inc = False
                        current_x += tile_size
                    if outer_inc:
                        current_x += tile_size
                current_y += tile_size
                current_x = 0
            print(frames)
        return wand_gif(frames, 100)

def get_closest(r,g,b):
    minimum = None, 255*3
    for block, color in blocks.items():
        rr,gg,bb = color
        diff = abs(rr-r) + abs(gg-g) + abs(bb-b)
        if diff <= minimum[1]:
            minimum = block, diff
    return minimum[0]

async def itid(url, size, outline=0):
    tile_size = 16
    async with aiohttp.ClientSession() as cs:
        async with cs.get(url) as r:
            image = Image.open(io.BytesIO(await r.read()))
            image = list(ImageSequence.Iterator(image))[0].convert('RGBA')
            image = ImageOps.contain(image, (size*tile_size,size*tile_size))
    with Image.new('RGBA', (image.width, image.height), (0,0,0,255)) as image2:
        draw = ImageDraw.Draw(image2)
        i = 0
        while i < image.height:
            j = 0
            while j < image.width:
                draw.rectangle([j, i, j+tile_size, i+tile_size], image.getpixel((j,i)), (0,0,0,255), int(outline/2))
                j += tile_size
            i += tile_size
    i = io.BytesIO()
    image2.save(i, format='PNG')
    i.seek(0)
    return i

async def twist(url):
    async with aiohttp.ClientSession() as cs:
        async with cs.get(url) as r:
            image = Image.open(io.BytesIO(await r.read()))
            image = list(ImageSequence.Iterator(image))[0].convert('RGBA')
    frames = [image]
    for i in range(0, 360, 8):
        image = image.copy().rotate(8)
        frames.append(image)
    return wand_gif(frames + frames[1:-1][::-1], 10)

class Imaging(commands.Cog):
    async def emboss(self, *, url:str):
        return await emboss(url)
    
    async def blur(self, *, url:str):
        return await blur(url)
    
    async def rectangle(self, *, x1:int, y1:int, x2:int, y2:int, color:str="green", image=None):
        return await rectangle(x1,y1,x2,y2,color,image)
    
    async def ellipse(self, *, x1:int, y1:int, x2:int, y2:int, color:str="green", image=None):
        return await ellipse(x1,y1,x2,y2,color,image)
    
    async def isod2d(self, *, input:str, gif=False):
        return await isod2d(input, gif)
    
    async def itid(self, *, url:str, size:int=64, outline:int=0):
        return await itid(url, size, outline)
    
    async def wawa(self, *, text:str):
        return await wawa(text)
    
    async def twist(self, *, url:str):
        return await twist(url)
    
    @commands.command()
    async def control_point(self, ctx):
        #just used as a control point to access this cog
        pass

async def async_setup(bot):
    await bot.add_cog(Imaging(bot))

def setup(bot):
    return async_setup(bot)
