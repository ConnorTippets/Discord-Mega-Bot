from PIL import Image, ImageFont, ImageDraw
import io
from pilmoji import Pilmoji

def google(text):
  with Image.open('./Pillow/Placeholders/google.png') as im:
    font = ImageFont.truetype('arial.ttf', size=13)
    with Pilmoji(im) as pilmoji:
      pilmoji.text((95, round(im.height/2)+6), text, fill=(0, 0, 0), font=font)
    i = io.BytesIO()
    im.save(i, format='PNG')
    i.seek(0)
  return i
