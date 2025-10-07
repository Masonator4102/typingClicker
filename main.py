
import pygame
import random
from collections import deque


#pygame setup
pygame.init()
running = True


#setting up render surface
renderWidth, renderHeight = 192,108
renderSurface = pygame.Surface((renderWidth, renderHeight))


#setting up display window
displayWidth, displayHeight = 1920, 1080
screen = pygame.display.set_mode((displayWidth, displayHeight))


#Fonts
pixelifyFontPath = "resources/PixelifySans-SemiBold.ttf"
wordsFont = pygame.font.Font(pixelifyFontPath, size = 75)

#Colors
correctWordColor = (30,255,20)
incorrectWordColor = (255,30,20)
defaultWordColor = (0,0,0)

backgroundColor = (200,200,200)

#load images
deskImg = pygame.image.load('resources/desk.png')
frameImg = pygame.image.load('resources/frame.png')
allKeysImg = pygame.image.load('resources/allKeys.png')

#load all the Words
with open('resources/words.txt', 'r') as f:
    WORDS = f.read().split()

#========Variables========
nextWordsList = deque()
pastWordsList = deque()
nextWordsString = ""
pastWordsString = ""
typedBuffer = ""
currentWordPxLen = 0
pXsAdvanced = 0

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

#create a list of images tied to their respective letter
pressedLetterImgList = {}
for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" :
    pressedLetterImgList[letter] = pygame.image.load(f"resources/pressed{letter}.png")

pressedKeyImgList = {}
for key in ["Colon", "Comma", "Delete", "lShift", "Period", "Question", "Quote", "rShift", "Space"] :
    pressedKeyImgList[key] = pygame.image.load(f"resources/pressed{key}.png")

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

def grabWord():
    if not WORDS:
        return False
    return random.choice(WORDS)

def onSuccessfulTypedWord():
    global pastWordsList, nextWordsList, typedBuffer, pXsAdvanced
    if not nextWordsList:
        return
    word = nextWordsList.popleft()
    pastWordsList.append(word)

    # advance by the exact pixels of "word + space" (matches your per-char render)
    pXsAdvanced += wordsFont.size(word + " ")[0]

    typedBuffer = ""

    nextWordsList.append(grabWord())

def checkIfCurrentWordTyped(typedBuffer):
    currentWord = nextWordsList[0]
    if typedBuffer == currentWord + " ":
        onSuccessfulTypedWord()
    else:
        return

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
    nextWordsList.append(grabWord())

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
                    errorBoxX = getWordPxWidth(nextWordsList[0]) 
                    pygame.draw.rect(nextWordsSurface, incorrectWordColor, (errorBoxX + 10 , 70, 20, 10))
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
    if not pastWordsString:
        return pygame.Surface((1,100), pygame.SRCALPHA)
    return wordsFont.render(pastWordsString, True, defaultWordColor)

    cX = 0
    for c in pastWordsString:
        currentLetter = wordsFont.render(c, True, defaultWordColor)
        nextWordsSurface.blit(currentLetter, (cX, 0))
        cX += currentLetter.get_width()
    return nextWordsSurface

#Used to get half the current word's width to adjust where the nextWords surface is drawn
def getWordPxWidth(word):
    wordWidth = wordsFont.size(word)[0]
    return wordWidth

def getTextPxWidth(text):
    return sum(wordsFont.size(c)[0] for c in text)

#Called whenever a key is pressed down within running loop
def handleKeysDown(event):
    global typedBuffer

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
            onSuccessfulTypedWord()   # <-- bump scroll + move word + refill + clear buffer
        return

    ch = event.unicode
    if ch and ch != '\x08':
        typedBuffer += ch


while running:

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

    # derive scroll purely from what you actually rendered for "past"
    # (adds exactly one space of gap between past and current)
    has_past   = bool(pastWordsList)
    space_w    = wordsFont.size(" ")[0] if has_past else 0
    pXsAdvanced = pastWordsSurface.get_width() + space_w  # <-- recomputed, no accumulation drift

    anchorX = screen.get_width() // 2
    baseX   = anchorX - pXsAdvanced
    y       = 100

    # draw past first, then current/next
    screen.blit(pastWordsSurface, (baseX, y))
    screen.blit(nextWordsSurface, (baseX + pXsAdvanced, y))

    # (optional) caret to visualize the anchor
    # pygame.draw.rect(screen, (0,0,0), (anchorX, y+5, 2, 70))

    screen.blit(rightMask, (1100, 100))
    screen.blit(leftMask,(450,100))
    screen.blit(coverTextMask,(0,100))
    pygame.display.flip()


pygame.quit()
