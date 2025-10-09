
import pygame
import random
from collections import deque


#pygame setup
pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(64)
clock = pygame.time.Clock()
targetFPS = 60
running = True

#setting up render surface
renderWidth, renderHeight = 192,108
renderSurface = pygame.Surface((renderWidth, renderHeight))


#setting up display window
displayWidth, displayHeight = 1920, 1080
screen = pygame.display.set_mode((displayWidth, displayHeight))


#Setting up surface(s) on which we can display our particle effects.
particlesSurface = pygame.Surface((displayWidth, displayHeight), pygame.SRCALPHA)
particlesSurface.fill((0,0,0,0))

#Setting up surface(s) on which we can display our non typing words
otherTextSurface = pygame.Surface((displayWidth, displayHeight), pygame.SRCALPHA)
otherTextSurface.fill((0,0,0,0))

#Fonts
pixelifyFontPath = "resources/Fonts/PixelifySans-SemiBold.ttf"
wordsFont = pygame.font.Font(pixelifyFontPath, size = 75)
otherTextFont = pygame.font.Font(pixelifyFontPath, size = 50)
debugFont = pygame.font.Font(None, 24)

#Colors
correctWordColor = (30,255,20)
incorrectWordColor = (255,30,20)
defaultWordColor = (0,0,0)

backgroundColor = (200,200,200)

#load images
deskImg = pygame.image.load('resources/Sprites/desk.png')
frameImg = pygame.image.load('resources/Sprites/frame.png')
allKeysImg = pygame.image.load('resources/Sprites/allKeys.png')

#load sound effects
keyboardSounds = {}
for i in range(1,12):
    keyboardSounds[i] = pygame.mixer.Sound(f"resources/Audio/KeyboardSounds/keyDown/keyDown{i}.wav")
    keyboardSounds[i].set_volume(1.0)

for i in range(1,5):
    index = i + 11
    keyboardSounds[index] = pygame.mixer.Sound(f"resources/Audio/KeyboardSounds/spaceBar/spaceBar{i}.wav")
    keyboardSounds[index].set_volume(1.0)

successFulWordSound = pygame.mixer.Sound('resources/Audio/coinGet.wav')
successFulWordSound.set_volume(.3)

#load all the Words
with open('resources/WordBanks/words.txt', 'r') as f:
    WORDS = f.read().split()

# set to True to simulate an empty words list for testing
TEST_EMPTY_WORDS = False
if TEST_EMPTY_WORDS:
    WORDS = []

#========Variables========
nextWordsList = deque()
pastWordsList = deque()
nextWordsString = ""
pastWordsString = ""
typedBuffer = ""
currentWordPxLen = 0
baseX = displayWidth / 2
baseY = displayHeight/ 10
coinsOriginLoc = displayWidth/10, displayHeight/10


#Turn this on to get an FPS readout 
debugging = False


#Key and letter positions
letterKeyPositions = {
    pygame.K_a: (25, 71),
    pygame.K_b: (73, 82),
    pygame.K_c: (51, 82),
    pygame.K_d: (47, 71),
    pygame.K_e: (43, 60),
    pygame.K_f: (58, 71),
    pygame.K_g: (69, 71),
    pygame.K_h: (80, 71),
    pygame.K_i: (98, 60),
    pygame.K_j: (91, 71),
    pygame.K_k: (102, 71),
    pygame.K_l: (113, 71),
    pygame.K_m: (95, 82),
    pygame.K_n: (84, 82),
    pygame.K_o: (109, 60),
    pygame.K_p: (120, 60),
    pygame.K_q: (21, 60),
    pygame.K_r: (54, 60),
    pygame.K_s: (36, 71),
    pygame.K_t: (65, 60),
    pygame.K_u: (87, 60),
    pygame.K_v: (62, 82),
    pygame.K_w: (32, 60),
    pygame.K_x: (40, 82),
    pygame.K_y: (76, 60),
    pygame.K_z: (29, 82),    
}
otherKeyPositions = {
    pygame.K_BACKSPACE: (148, 49),
    pygame.K_SPACE:     (43, 93),
    pygame.K_PERIOD:    (117, 82),
    pygame.K_SLASH:     (128, 82),
    pygame.K_LSHIFT:    (5, 82),
    pygame.K_RSHIFT:    (139, 82),
    pygame.K_SEMICOLON: (124, 71),
    pygame.K_QUOTE:     (135, 71),
    pygame.K_COMMA:     (106, 82),    
}
otherKeyNames = {
    pygame.K_BACKSPACE: "Delete",
    pygame.K_SPACE:     "Space",
    pygame.K_PERIOD:    "Period",
    pygame.K_SLASH:     "Question",
    pygame.K_LSHIFT:    "lShift",
    pygame.K_RSHIFT:    "rShift",
    pygame.K_SEMICOLON: "Colon",
    pygame.K_QUOTE:     "Quote",
    pygame.K_COMMA:     "Comma",    
}

#####=========GAME STATE/PROGRESS VARIABLES==========######

totalMoney = 0
moneyPerKey = {
    "a" : 1,
    "A" : 1,
    "b" : 1,
    "B" : 1,
    "c" : 1,
    "C" : 1,
    "d" : 1,
    "D" : 1,
    "e" : 1,
    "E" : 1,
    "f" : 1,    
    "F" : 1,
    "g" : 1,
    "G" : 1,
    "h" : 1,
    "H" : 1,
    "i" : 1,
    "I" : 1,
    "j" : 1,
    "J" : 1,
    "k" : 1,
    "K" : 1,    
    "l" : 1,
    "L" : 1,
    "m" : 1,
    "M" : 1,
    "n" : 1,
    "N" : 1,
    "o" : 1,
    "O" : 1,
    "p" : 1,
    "P" : 1,
    "q" : 1,
    "Q" : 1,
    "r" : 1,
    "R" : 1,
    "s" : 1,
    "S" : 1,
    "t" : 1,
    "T" : 1,
    "u" : 1,
    "U" : 1,
    "v" : 1,
    "V" : 1,
    "w" : 1,
    "W" : 1,
    "x" : 1,
    "X" : 1,
    "y" : 1,
    "Y" : 1,
    "z" : 1,
    "Z" : 1,
    }    
    


#####==============CLASSES========================#####

#All purpose sprite class with support for color keys, see immediately below for useage
class SpriteSheet(object):

    def __init__ (self, filename):
        try:
            self.sheet = pygame.image.load(filename).convert_alpha()
        except:
            print("Unable to load spritesheet image: "), filename
            raise SystemExit

    def image_at(self, rectangle, colorkey = None):
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size, flags = pygame.SRCALPHA)
        image.blit(self.sheet,(0,0), rect)
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey,pygame.RLEACCEL)
        return image

    def images_at(self, rects, colorkey = None):
        return [self.image_at(rect, colorkey) for rect in rects]

    def load_strip(self, rect, image_count, colorkey = None):
        tups = [(rect[0] + rect[2]*x, rect[1], rect[2], rect[3])
            for x in range(image_count)]
        return self.images_at(tups, colorkey)



#Class to hold the coin sprite and handle animating/updating the coin particles
class CoinSprite(pygame.sprite.Sprite):

    spriteSheet = SpriteSheet("resources/Sprites/coinSpriteSheet.png")
    FRAMES = spriteSheet.load_strip((0, 0, 20, 20), image_count=8, colorkey=-1)

    def __init__(self, x, y):
        super().__init__()
        self.frames = self.FRAMES           
        self.frame_index = 0.0
        self.xNudge = random.uniform(-25, 25)
        self.fps = 16                

        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=(x + self.xNudge, y))
        self.vx = self.xNudge * 0.25
        self.vy = random.uniform(-8,-15)
        self.gravity = .7

    def update(self, dt, screen_rect):
        # physics
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.vy += self.gravity

        # time-based animation
        self.frame_index = (self.frame_index + self.fps * dt) % len(self.frames)
        self.image = self.frames[int(self.frame_index)]

        # cull off-screen

        if self.rect.right < 0 or self.rect.left > screen_rect.width or self.rect.bottom < -300 or self.rect.top > screen_rect.height:
            self.kill()

coinsSpriteGroup = pygame.sprite.Group()

#create a list of images tied to their respective letter
pressedLetterImgList = {}
for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" :
    pressedLetterImgList[letter] = pygame.image.load(f"resources/Sprites/pressed{letter}.png")

pressedKeyImgList = {}
for key in ["Colon", "Comma", "Delete", "lShift", "Period", "Question", "Quote", "rShift", "Space"] :
    pressedKeyImgList[key] = pygame.image.load(f"resources/Sprites/pressed{key}.png")

#When a keycode enters, a plain text version returns
def letterLabelfromKey(keycode):
    index = keycode - pygame.K_a
    if 0 <= index < 26:
        return chr(ord("A") + index)
    return None

#Master dictionary to hold all key(board) sprites and their positions
keySprites = {}

for i, pos in letterKeyPositions.items():
    label = letterLabelfromKey(i)
    img = pressedLetterImgList[label]
    keySprites[i] = (img, pos)

for i, pos in otherKeyPositions.items():
    label = otherKeyNames[i]
    img = pressedKeyImgList[label]
    keySprites[i] = (img, pos)


def spawnCoin(x, y, count):
    for _ in range(count):
        coinsSpriteGroup.add(CoinSprite(x,y))

def grabWord():
    if not WORDS:
        return None
    return random.choice(WORDS)


def calculateMoney(word):
    wordScore = 0

    for c in word:
        if(c in moneyPerKey):
            wordScore += moneyPerKey[c]
        else:
            print("you messed up")

    return wordScore


def onSuccessfulTypedWord():

    successFulWordSound.play()
    global pastWordsList, nextWordsList, typedBuffer, totalMoney
    if not nextWordsList:
        return
    word = nextWordsList.popleft()
    pastWordsList.append(word)


    spawnCoin(baseX + getWordPxWidth(nextWordsList[0]) / 2, baseY + 50, calculateMoney(typedBuffer))
    totalMoney +=  calculateMoney(typedBuffer)
    totalMoneyText = otherTextFont.render(str(totalMoney), True, (0,0,0,0))
    otherTextSurface.fill((0,0,0,0))
    otherTextSurface.blit(totalMoneyText, (10,10))

    typedBuffer = ""

    new_word = grabWord()
    if new_word is not None:
        nextWordsList.append(new_word)

def setPressedKeys(keys):

    for i, (img, pos) in keySprites.items():
        if keys[i]:
            renderSurface.blit(img,pos)

def createFadeMask(width, height, fadeOut):
    maskSurface = pygame.Surface((width, height), pygame.SRCALPHA)
    r,g,b = backgroundColor
    for x in range(width):
        if(fadeOut):
            t = x / (width - 1)
            a = int(255 * t)
            pygame.draw.line(maskSurface, (r,g,b,a), (x,0), (x,height-1))
        else:
            t = x / (width - 1)
            a = int(255 * (1-t))
            pygame.draw.line(maskSurface, (r,g,b,a), (x,0), (x,height-1))        
    return maskSurface

#Generate the initial list of words and sets the currentWord to the first in the list
for i in range(10):
    word = grabWord()
    if word is not None:
        nextWordsList.append(word)

#Generate the masks that create the fade effect on the text
rightMask = createFadeMask(900,100, True)
leftMask = createFadeMask(400,100, False)
coverTextMask = pygame.surface.Surface((450,100))
coverTextMask.fill((backgroundColor))


#Draws all the words in nextWordsList on a single surface to put on the screen. Also creates a string containing all the letters on the surface
def drawNextWords():
    global nextWordsString
    nextWordsString = " ".join(nextWordsList) + " "
    surfaceWidth, _ = wordsFont.size(nextWordsString)

    nextWordsSurface = pygame.Surface((surfaceWidth, 100), pygame.SRCALPHA)
    nextWordsSurface.fill((0,0,0,0))

    cX = 0
    for i, ch in enumerate(nextWordsString):
        if i < len(typedBuffer):
            if not ch == " ":
                color = correctWordColor 
                if ch == typedBuffer[i]:            
                    color = correctWordColor 
                else:
                    color = incorrectWordColor
            else:
                if ch == typedBuffer[i]:
                    color = correctWordColor 
                else:
                    if nextWordsList:
                        errorBoxX = getWordPxWidth(nextWordsList[0]) * 1.02
                        errorBoxW = getWordPxWidth(" ") + 5
                        pygame.draw.rect(nextWordsSurface, incorrectWordColor, (errorBoxX, 70, errorBoxW, 10))
                    color = incorrectWordColor
        else:
            color = defaultWordColor

        currentLetter = wordsFont.render(ch, True, color)   
        nextWordsSurface.blit(currentLetter, (cX, 0))     
        cX += currentLetter.get_width()      

    return nextWordsSurface  

#Draws all the words in pastWordsList on a single surface to put on the screen.
def drawPastWords():
    global pastWordsString
    pastWordsString = " ".join(pastWordsList)
    surfaceWidth, _ = wordsFont.size(nextWordsString)

    pastWordsSurface = pygame.Surface((surfaceWidth, 100), pygame.SRCALPHA)
    pastWordsSurface.fill((0,0,0,0))

    pastWordsText = wordsFont.render(pastWordsString, True, defaultWordColor)
    pastWordsSurface.blit(pastWordsText, (0,0))

    #pop items from pastWordsList when they're no longer shown to prevent issues with surface placement
    if getWordPxWidth(pastWordsString) > displayWidth/2 - 10:
        pastWordsList.popleft()

    return pastWordsSurface

#Used to get half the current word's width to adjust where the nextWords surface is drawn
def getWordPxWidth(word):
    wordWidth = wordsFont.size(word)[0]
    return wordWidth

def getTextPxWidth(text):
    return sum(wordsFont.size(c)[0] for c in text)

def playKeySound(event):

    if not event.key == pygame.K_SPACE:
        choice = random.randint(1,11)
        pygame.mixer.Sound.play(keyboardSounds[choice])
    else:
        choice = random.randint(12,15)
        pygame.mixer.Sound.play(keyboardSounds[choice])


#Called whenever a key is pressed down within running loop
def handleKeysDown(event):
    global typedBuffer

    playKeySound(event)

    mods = pygame.key.get_mods()
    ctrl_down = mods & pygame.KMOD_LCTRL or mods & pygame.KMOD_CTRL

    if event.key == pygame.K_ESCAPE:
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        return

    if event.key == pygame.K_BACKSPACE:
        if not ctrl_down:
            typedBuffer = typedBuffer[:-1]
        else:
            if " " in typedBuffer:
                cutIndex = typedBuffer.rfind(" ")
                typedBuffer = typedBuffer[:cutIndex + 1]
            else:
                typedBuffer = ""
        return

    if event.key == pygame.K_SPACE:
        if nextWordsList and typedBuffer == nextWordsList[0]:
            onSuccessfulTypedWord()
        else:
            typedBuffer += " "
        return

    ch = event.unicode
    if ch and ch != '\x08':
        typedBuffer += ch


while running:

    dt = clock.tick(targetFPS) / 1000
    screen_rect = screen.get_rect()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            handleKeysDown(event)
                
    
    renderSurface.fill((200,200,200))
    renderSurface.blit(frameImg, (0, 10))
    renderSurface.blit(allKeysImg, (0,10))

    keys = pygame.key.get_pressed()
    setPressedKeys(keys)

    #scale the renderSurface up so it fills the screen
    scaledSurface = pygame.transform.scale(renderSurface, (displayWidth, displayHeight))
    screen.blit(scaledSurface, (0, 0))

    # build the text surfaces once per frame
    pastWordsSurface = drawPastWords()
    nextWordsSurface = drawNextWords()

    # draw the word surfaces to the screen
    screen.blit(pastWordsSurface, (baseX - getWordPxWidth(pastWordsString + " "), baseY))
    screen.blit(nextWordsSurface, (baseX, baseY))

    # if testing (or actual) empty words, show a friendly message
    if not WORDS and not nextWordsList:
        msg_surface = wordsFont.render("No words found", True, (0,0,0))
        mx = (screen.get_width() - msg_surface.get_width()) // 2
        my = baseY + 120
        screen.blit(msg_surface, (mx, my))

    screen.blit(rightMask, (1100, baseY))
    screen.blit(leftMask,(450,baseY))
    screen.blit(coverTextMask,(0,100))

    #Blit the particle surface to the screen
    coinsSpriteGroup.update(dt, screen_rect)
    particlesSurface.fill((0,0,0,0))
    coinsSpriteGroup.draw(particlesSurface)

    #Debug info will be shown if debugging boolean switch on
    if debugging:
        fps_text = debugFont.render(f"FPS: {clock.get_fps():.1f}", True, (200, 255, 200))
        screen.blit(fps_text, (0,0))
    screen.blit(otherTextSurface,(0,0))
    screen.blit(particlesSurface,(0,0))


    pygame.display.flip()


pygame.quit()
