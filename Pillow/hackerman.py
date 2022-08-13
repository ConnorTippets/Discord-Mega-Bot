from PIL import Image, ImageFont, ImageDraw
import io
import textwrap

def hackerman(text):
    with Image.new('RGB', (600, 400), color='black') as im:
        draw = ImageDraw.Draw(im)
        font = ImageFont.truetype("./Pillow/Fonts/VT323-Regular.ttf", 30)
        draw.text((6, 6), '\n'.join([textwrap.fill(i, 48) if len(i) > 48 else i for i in text.split('\n')]), fill=(0, 128, 0), font=font)
        i = io.BytesIO()
        im.save(i, format="PNG")
        i.seek(0)
    return i
