#import math, pygame, sys
import math, io
from PIL import Image, ImageDraw
x = 400
y = 0
z = 300
vspd = 0
canJump = False

pWidth = 50
pHeight = 50

blink = 0
space = False
#pygame.init()
#clock = pygame.time.Clock()
#screen = pygame.display.set_mode((800,600))
fpang = 0

def gameloop():
    gameLogic()
    paintScreen()

def fpDrawPillar(prX, prY, prZ, prW, prH, prL, image):
    propEnds = 0.03
    propIn = 0.66

    playerHeight = 100
    prY = playerHeight - prH - prY

    drawPrism(prX, prY, prZ, prW, prH * propEnds, prL, image)
    drawPrism(prX + prW * (1 - propIn)/2, prY + prH * propEnds, prZ + prL * (1 - propIn)/2, prW * propIn, prH - prH * propEnds, prL * propIn, image)
    drawPrism(prX, prY + prH - prH * propEnds, prZ, prW, prH * propEnds, prL, image)

def drawPrism(prX, prY, prZ, prW, prH, prL, image):
    draw3dLine(prX, prY, prZ, prX, prY, prZ + prL, image)
    draw3dLine(prX, prY, prZ, prX, prY + prH, prZ, image)
    draw3dLine(prX, prY + prH, prZ, prX, prY + prH, prZ + prL, image)
    draw3dLine(prX, prY, prZ + prL, prX, prY + prH, prZ + prL, image)

    draw3dLine(prX + prW, prY, prZ, prX + prW, prY, prZ + prL, image)
    draw3dLine(prX + prW, prY, prZ, prX + prW, prY + prH, prZ, image)
    draw3dLine(prX + prW, prY + prH, prZ, prX + prW, prY + prH, prZ + prL, image)
    draw3dLine(prX + prW, prY, prZ + prL, prX + prW, prY + prH, prZ + prL, image)

    draw3dLine(prX, prY, prZ, prX + prW, prY, prZ, image)
    draw3dLine(prX, prY + prH, prZ, prX + prW, prY + prH, prZ, image)
    draw3dLine(prX, prY, prZ + prL, prX + prW, prY, prZ + prL, image)
    draw3dLine(prX, prY + prH, prZ + prL, prX + prW, prY + prH, prZ + prL, image)

def draw3dLine(x1, y1, z1, x2, y2, z2, image):
    centerOfScreenX = 400
    centerOfScreenY = 300

    x1Diff = x1 - x
    y1Diff = y1 - y
    z1Diff = z1 - z
    x2Diff = x2 - x
    y2Diff = y2 - y
    z2Diff = z2 - z

    translatedX1 = x1Diff * math.cos(-fpang) + z1Diff * math.sin(-fpang)
    translatedZ1 = z1Diff * math.cos(-fpang) - x1Diff * math.sin(-fpang)
    translatedX2 = x2Diff * math.cos(-fpang) + z2Diff * math.sin(-fpang)
    translatedZ2 = z2Diff * math.cos(-fpang) - x2Diff * math.sin(-fpang)
	
    if translatedZ1 < 0 or translatedZ2 < 0:
        return
	
    screenDistance = 400

    try:
        dispX1 = (translatedX1 / translatedZ1) * screenDistance + centerOfScreenX
    except:
        return
    try:
        dispY1 = (y1Diff / translatedZ1) * screenDistance + centerOfScreenY
    except:
        return
    try:
        dispX2 = (translatedX2 / translatedZ2) * screenDistance + centerOfScreenX
    except:
        return
    try:
        dispY2 = (y2Diff / translatedZ2) * screenDistance + centerOfScreenY
    except:
        return
    draw = ImageDraw.Draw(image)
    draw.line([dispX1, dispY1, dispX2, dispY2], (0,0,0), 1)

def controlLogic():
    global fpang, x, z
    walkSpd = 5
    turnSpd = 0.03
    if up:
        x += math.sin(fpang) * walkSpd
        z += math.cos(fpang) * walkSpd
    elif down:
        x -= math.sin(fpang) * walkSpd
        z -= math.cos(fpang) * walkSpd
    if right:
        fpang += turnSpd
    elif left:
        fpang -= turnSpd

def gameLogic():
    controlLogic()

def paintScreen(xx=400, zz=300, ang=0):
    global x, y, fpang
    x,z,fpang=xx,zz,ang
    color = (102, 153, 102)
    image = Image.new('RGB', (800, 600), color)
    #screen.fill(color)
    for i in range(8):
        fpDrawPillar(550, 0, 200 + 400 * i, 50, 300, 50, image)
        fpDrawPillar(200, 0, 200 + 400 * i, 50, 300, 50, image)
    i = io.BytesIO()
    image.save(i, format='PNG')
    i.seek(0)
    return i
    #pygame.display.flip()

#while True:
#    global left, right, up, down
#    left,right,up,down = False,False,False,False
#    for event in pygame.event.get():
#        if event.type == pygame.QUIT:
#            pygame.quit()
#            sys.exit()
#    keys = pygame.key.get_pressed()
#    if keys[pygame.K_LEFT]:
#        left = True
#    if keys[pygame.K_RIGHT]:
#        right = True
#    if keys[pygame.K_UP]:
#        up = True
#    if keys[pygame.K_DOWN]:
#        down = True
#    gameloop()
#    clock.tick(60)
