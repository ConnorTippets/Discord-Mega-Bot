from PIL import Image, ImageFont, ImageDraw, ImageOps
import discord
import io, os

async def caption(author, text):
    with Image.open(io.BytesIO(await author.avatar.read())) as im1:
      with Image.new('RGB', (im1.width, round(im1.height/4)), (255, 255, 255, 255)) as im2:
          draw = ImageDraw.Draw(im2)
          font = ImageFont.truetype("./Pillow/Fonts/VT323-Regular.ttf", 30)
          draw.text((6, 6), text, fill=(0, 0, 0, 255), font=font)
          im1.paste(im2)
          i = io.BytesIO()
          im1.save(i, format='PNG')
          i.seek(0)
    return i

async def kindle(image):
    im1 = Image.open(os.getcwd()+"\\kindleImage.png")
    with Image.open(io.BytesIO((image.fp.read() if not hasattr(image, "read") else (await image.read())))) as im2:
        im2 = im2.resize((2246, 1657), 2)
        im2 = ImageOps.grayscale(im2)
        im1.paste(im2, (215, 212))
        i = io.BytesIO()
        im1.save(i, format='PNG')
        i.seek(0)
    return i

async def display(text, member):
    im2 = Image.open(io.BytesIO(await member.avatar.read())).convert('RGBA')
    font1 = ImageFont.truetype("./Pillow/Fonts/Roboto/Roboto-Regular.ttf", 100)
    with Image.new('RGBA', (im2.width,im2.height), (47,49,54,255)) as im1:
        draw = ImageDraw.Draw(im1)
        width = draw.textlength((text if text else ""), font1) + im2.width + 90
        height = im2.height
        size = (width, height)
    size = (int(size[0]), int(size[1]))
    with Image.new('RGBA', size, (47,49,54,255)) as im1:
        mask_im = Image.new("L", (im2.width, size[1]), 0)
        draw = ImageDraw.Draw(mask_im)
        draw.ellipse((0, 0, im2.width, size[1]), fill=255)
        im1.paste(im2, mask_im)
        im3 = Image.new("RGBA", (im2.width*2, round(size[1]/2)), (47,49,54,255))
        draw = ImageDraw.Draw(im3)
        draw.text((0,0), (text if text else ""), fill=(129,130,135,255), font=font1)
        im1.paste(im3, (im2.width+45, round(size[1]/2)))
        i = io.BytesIO()
        im1.save(i, format='PNG')
        i.seek(0)
    return i
