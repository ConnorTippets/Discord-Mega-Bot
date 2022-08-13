from PIL import Image, ImageFilter
import io

async def emboss(author):
    with Image.open(io.BytesIO(await author.avatar.read())) as im:
        im = im.filter(ImageFilter.EMBOSS)
        i = io.BytesIO()
        im.save(i, 'PNG')
        i.seek(0)
    return i

async def blur(author):
    with Image.open(io.BytesIO(await author.avatar.read())) as im:
        im = im.filter(ImageFilter.BLUR)
        i = io.BytesIO()
        im.save(i, 'PNG')
        i.seek(0)
    return i
