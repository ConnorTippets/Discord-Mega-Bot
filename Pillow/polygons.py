from PIL import ImageDraw, Image, ImageColor
import io

def color_to_rgb(color):
    return ImageColor.getrgb(color)

async def rectangle(x1, y1, x2, y2, color, image=None):
    im = None
    if image:
        im = Image.open(image)
    else:
        im = Image.new('RGB', (600, 400))
    draw = ImageDraw.Draw(im)
    draw.rectangle([(x1, y1), (x2, y2)], fill=color_to_rgb(color))
    i = io.BytesIO()
    im.save(i, 'PNG')
    i.seek(0)
    return i

def ellipse(x1, y1, x2, y2, color, *, image=None):
    im = None
    if image:
        im = Image.open(image)
    else:
        im = Image.new('RGB', (600, 400))
    draw = ImageDraw.Draw(im)
    draw.ellipse([(x1, y1, x2, y2)], fill=color_to_rgb(color))
    i = io.BytesIO()
    im.save(i, 'PNG')
    i.seek(0)
    return i
