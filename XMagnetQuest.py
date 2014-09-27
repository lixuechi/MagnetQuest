# THANKS TO Al Sweigart al@inventwithpython.com
# designer: Tawei Chiang, Cheng Zhang
# programmer: Xuechi Li
# graphic artist: LIngshu Yang
# audio artist: Tian Zhou
# from March to April in 2013
# last edit: Jan 30, 2014
# description: eat as many stars as possible to gain scores
#              avoid eating garbages, they will slow your speed
#              water drops can speed you up 
import random, sys, time, math, pygame
from pygame.locals import *

FPS = 30 # frames per second to update the screen
WINWIDTH = 640 # width of the program's window, in pixels
WINHEIGHT = 480 # height in pixels
HALF_WINWIDTH = int(WINWIDTH / 2)
HALF_WINHEIGHT = int(WINHEIGHT / 2)


WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
PINK = (223,159,160)

CAMERASLACK = 90     # how far from the center the ball moves before moving the camera
MOVERATE = 9         # how fast the player moves

ADDSPEED = 10        # improve the current speed by 10pps
STARTSCORE = 0
STARTSIZE = 30       # how big the ball starts off
STARTSPEED = 20

INVULNTIME = 2       # how long the player is invulnerable after being hit in seconds
GAMEOVERTIME = 4     # how long the "game over" text stays on the screen in seconds

PLUSFIVE = 5   # plus 5 scores

NUMCLEANUP = 3  # number of cleanups in the active area
NUMTREASURE = 30   # number of treasures in the active area
NUMGARBAGE = 30    # number of garbages in the active area
MINSPEED = 3 # slowest speed
MAXSPEED = 7 # fastest speed
DIRCHANGEFREQ = 2    # % chance of direction change per frame
LEFT = 'left'
RIGHT = 'right'

#....................................................................................................................................#

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, L_BALL_IMG, R_BALL_IMG, GAR_IMG, TRE_IMG, CLE_IMG, BG_IMG, TRE_SE

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    #pygame.display.set_icon(pygame.image.load('gameicon.png'))
    DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT))
    pygame.display.set_caption('Magnet Quest')
    BASICFONT = pygame.font.Font('freesansbold.ttf', 32)

    # load the image files
    L_BALL_IMG = pygame.image.load('angryball.png')
    R_BALL_IMG = pygame.transform.flip(L_BALL_IMG, True, False)
    GAR_IMG = pygame.image.load('garbage.png')
    
    TRE_IMG  = pygame.image.load('treasure.png')
    CLE_IMG  = pygame.image.load('cleanup.png')

    BG_IMG = pygame.image.load('bgimg.jpg')
    
    # load the sound files
    #TRE_SE = pygame.mixer.Sound('treasure.wav')

    
    while True:
        runGame()
        


def runGame():
    
    
    # set up variables for the start of a new game
    invulnerableMode = False  # if the player is invulnerable
    invulnerableStartTime = 0 # time the player became invulnerable
    gameOverMode = False      # if the player has lost
    gameOverStartTime = 0     # time the player lost
   

    # create the surfaces to hold game text
    gameOverSurf = BASICFONT.render('Game Over', True, WHITE)
    gameOverRect = gameOverSurf.get_rect()
    gameOverRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

   

    # camerax and cameray are the top left of where the camera view is
    camerax = 0
    cameray = 0


    cleanupObjs = [] # stores all the cleanup objects
    treasureObjs = [] # stores all the treasure objects
    garbageObjs = [] # stores all the non-player garbage objects
    # stores the player object:
    playerObj = {'surface': pygame.transform.scale(L_BALL_IMG, (STARTSIZE, STARTSIZE)),
                 'facing': LEFT,
                 'size': STARTSIZE,
                 'x': HALF_WINWIDTH,
                 'y': HALF_WINHEIGHT,
                 'speed': STARTSPEED,
                 'score': STARTSCORE}

    moveLeft  = False
    moveRight = False
    moveUp    = False
    moveDown  = False



    while True: # main game loop
        # Check if we should turn off invulnerability
        if invulnerableMode and time.time() - invulnerableStartTime > INVULNTIME:
            invulnerableMode = False

        # move all the garbages
        for gObj in garbageObjs:
            # move the garbage
            gObj['x'] += gObj['movex']
            gObj['y'] += gObj['movey']
            

            # random chance they change direction
            if random.randint(0, 99) < DIRCHANGEFREQ:
                gObj['movex'] = getRandomVelocity()
                gObj['movey'] = getRandomVelocity()
                if gObj['movex'] > 0: # faces right
                    gObj['surface'] = pygame.transform.scale(GAR_IMG, (gObj['width'], gObj['height']))
                else: # faces left
                    gObj['surface'] = pygame.transform.scale(GAR_IMG, (gObj['width'], gObj['height']))


        # move all the treasures
        for tObj in treasureObjs:
            # move the treasure
            tObj['x'] += tObj['movex']
            tObj['y'] += tObj['movey']

            # random chance they change direction
            if random.randint(0, 99) < DIRCHANGEFREQ:
                tObj['movex'] = getRandomVelocity()
                tObj['movey'] = getRandomVelocity()
                if tObj['movex'] > 0: # faces right
                    tObj['surface'] = pygame.transform.scale(TRE_IMG, (tObj['width'], tObj['height']))
                else: # faces left
                    tObj['surface'] = pygame.transform.scale(TRE_IMG, (tObj['width'], tObj['height']))


        # move all the cleanups
        for cObj in cleanupObjs:
            # move the cleanup
            cObj['x'] += cObj['movex']
            cObj['y'] += cObj['movey']

            # random chance they change direction
            if random.randint(0, 99) < DIRCHANGEFREQ:
                cObj['movex'] = getRandomVelocity()
                cObj['movey'] = getRandomVelocity()
                if cObj['movex'] > 0: # faces right
                    cObj['surface'] = pygame.transform.scale(CLE_IMG, (cObj['width'], cObj['height']))
                else: # faces left
                    cObj['surface'] = pygame.transform.scale(CLE_IMG, (cObj['width'], cObj['height']))

        # go through all the objects and see if any need to be deleted.
   
        for i in range(len(garbageObjs) - 1, -1, -1):
            if isOutsideActiveArea(camerax, cameray, garbageObjs[i]):
                del garbageObjs[i]


        for i in range(len(treasureObjs) - 1, -1, -1):
            if isOutsideActiveArea(camerax, cameray, treasureObjs[i]):
                del treasureObjs[i]


        for i in range(len(cleanupObjs) - 1, -1, -1):
            if isOutsideActiveArea(camerax, cameray, cleanupObjs[i]):
                del cleanupObjs[i]

        # add more objects if we don't have enough.

        while len(garbageObjs) < NUMGARBAGE:
            garbageObjs.append(makeNewGarbage(camerax, cameray))


        while len(treasureObjs) < NUMTREASURE:
            treasureObjs.append(makeNewTreasure(camerax, cameray))


        while len(cleanupObjs) < NUMCLEANUP:
            cleanupObjs.append(makeNewCleanup(camerax, cameray))

        # adjust camerax and cameray if beyond the "camera slack"
        playerCenterx = playerObj['x'] + int(playerObj['size'] / 2)
        playerCentery = playerObj['y'] + int(playerObj['size'] / 2)
        if (camerax + HALF_WINWIDTH) - playerCenterx > CAMERASLACK:
            camerax = playerCenterx + CAMERASLACK - HALF_WINWIDTH
        elif playerCenterx - (camerax + HALF_WINWIDTH) > CAMERASLACK:
            camerax = playerCenterx - CAMERASLACK - HALF_WINWIDTH
        if (cameray + HALF_WINHEIGHT) - playerCentery > CAMERASLACK:
            cameray = playerCentery + CAMERASLACK - HALF_WINHEIGHT
        elif playerCentery - (cameray + HALF_WINHEIGHT) > CAMERASLACK:
            cameray = playerCentery - CAMERASLACK - HALF_WINHEIGHT

        # display the background image
        DISPLAYSURF.blit(BG_IMG, (0,0))

        # play the background music
        #pygame.mixer.music.load('bgmusic.mp3')
        #pygame.mixer.music.play(-1, 0.0)


        # draw the other garbages
        for gObj in garbageObjs:
            gObj['rect'] = pygame.Rect( (gObj['x'] - camerax,
                                         gObj['y'] - cameray,
                                         gObj['width'],
                                         gObj['height']) )
            DISPLAYSURF.blit(gObj['surface'], gObj['rect'])


        # draw the other treasures
        for tObj in treasureObjs:
            tObj['rect'] = pygame.Rect( (tObj['x'] - camerax,
                                         tObj['y'] - cameray,
                                         tObj['width'],
                                         tObj['height']) )
            DISPLAYSURF.blit(tObj['surface'], tObj['rect'])


        # draw the other cleanups
        for cObj in cleanupObjs:
            cObj['rect'] = pygame.Rect( (cObj['x'] - camerax,
                                         cObj['y'] - cameray,
                                         cObj['width'],
                                         cObj['height']) )
            DISPLAYSURF.blit(cObj['surface'], cObj['rect'])


        # draw the player ball
        flashIsOn = round(time.time(), 1) * 10 % 2 == 1
        if not gameOverMode and not (invulnerableMode and flashIsOn):
            playerObj['rect'] = pygame.Rect( (playerObj['x'] - camerax,
                                              playerObj['y'] - cameray,
                                              playerObj['size'],
                                              playerObj['size']) )
            DISPLAYSURF.blit(playerObj['surface'], playerObj['rect'])


        # draw the speed meter
        drawSpeedMeter(playerObj['speed'])

        # draw the score
        drawScore(playerObj['score'])

        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                terminate()

            elif event.type == KEYDOWN:
                if event.key in (K_UP, K_w):
                    moveDown = False
                    moveUp = True
                elif event.key in (K_DOWN, K_s):
                    moveUp = False
                    moveDown = True
                elif event.key in (K_LEFT, K_a):
                    moveRight = False
                    moveLeft = True
                    if playerObj['facing'] != LEFT: # change player image
                        playerObj['surface'] = pygame.transform.scale(L_BALL_IMG, (playerObj['size'], playerObj['size']))
                    playerObj['facing'] = LEFT
                elif event.key in (K_RIGHT, K_d):
                    moveLeft = False
                    moveRight = True
                    if playerObj['facing'] != RIGHT: # change player image
                        playerObj['surface'] = pygame.transform.scale(R_BALL_IMG, (playerObj['size'], playerObj['size']))
                    playerObj['facing'] = RIGHT
                elif event.key == K_r:
                    return

            elif event.type == KEYUP:
                # stop moving the player's squirrel
                if event.key in (K_LEFT, K_a):
                    moveLeft = False
                elif event.key in (K_RIGHT, K_d):
                    moveRight = False
                elif event.key in (K_UP, K_w):
                    moveUp = False
                elif event.key in (K_DOWN, K_s):
                    moveDown = False

                elif event.key == K_ESCAPE:
                    terminate()

        if not gameOverMode:
            # actually move the player
            if moveLeft:
                playerObj['x'] -= playerObj['speed']
            if moveRight:
                playerObj['x'] += playerObj['speed']
            if moveUp:
                playerObj['y'] -= playerObj['speed']
            if moveDown:
                playerObj['y'] += playerObj['speed']

            

            # check if the player has collided with any garbages
            for i in range(len(garbageObjs)-1, -1, -1):
                gaObj = garbageObjs[i]
                if 'rect' in gaObj and playerObj['rect'].colliderect(gaObj['rect']):
                    # a player/garbage collision has occurred

                    
                    # player eats the garbage
                    playerObj['size'] += int( (gaObj['width'] * gaObj['height'])**0.2 ) + 1
                    del garbageObjs[i]
                    playerObj['speed'] -= 1
                    if playerObj['speed'] == 0:
                        gameOverMode = True
                        gameOverStartTime = time.time()

                    if playerObj['facing'] == LEFT:
                        playerObj['surface'] = pygame.transform.scale(L_BALL_IMG, (playerObj['size'], playerObj['size']))
                    if playerObj['facing'] == RIGHT:
                        playerObj['surface'] = pygame.transform.scale(R_BALL_IMG, (playerObj['size'], playerObj['size']))

                    


            # check if the player has collided with any treasures
            for i in range(len(treasureObjs)-1, -1, -1):
                trObj = treasureObjs[i]
                if 'rect' in trObj and playerObj['rect'].colliderect(trObj['rect']):
                    # a player/treasure collision has occurred
                    #sound = TRE_SE
                    
                    # player eats the treasure
                    
                    del treasureObjs[i]
                    playerObj['score'] += PLUSFIVE
                    

                    if playerObj['facing'] == LEFT:
                        playerObj['surface'] = pygame.transform.scale(TRE_IMG, (playerObj['size'], playerObj['size']))
                    if playerObj['facing'] == RIGHT:
                        playerObj['surface'] = pygame.transform.scale(TRE_IMG, (playerObj['size'], playerObj['size']))

                    




            # check if the player has collided with any cleanups
            for i in range(len(cleanupObjs)-1, -1, -1):
                clObj = cleanupObjs[i]
                if 'rect' in clObj and playerObj['rect'].colliderect(clObj['rect']):
                    # a player/cleanup collision has occurred

                    
                    # player eats the cleanup
                    
                    del cleanupObjs[i]
                    if playerObj['speed'] <= 10:
                        playerObj['speed'] += ADDSPEED
                        playerObj['size'] -= ADDSPEED
                    else:
                        playerObj['speed'] = 20
                        playerObj['size'] = 30

                    if playerObj['facing'] == LEFT:
                        playerObj['surface'] = pygame.transform.scale(CLE_IMG, (playerObj['size'], playerObj['size']))
                    if playerObj['facing'] == RIGHT:
                        playerObj['surface'] = pygame.transform.scale(CLE_IMG, (playerObj['size'], playerObj['size']))

                    

                 
        else:
            # game is over, show "game over" text
            DISPLAYSURF.blit(gameOverSurf, gameOverRect)
            if time.time() - gameOverStartTime > GAMEOVERTIME:
                return # end the current game

        

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def drawScore(score):
    scoreSurf = BASICFONT.render('Score: %s' % (score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINWIDTH - 200, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

    

def drawSpeedMeter(currentSpeed):
    for i in range(currentSpeed): # draw pink speed bars
        pygame.draw.rect(DISPLAYSURF, PINK,   (15, 5 + (10 * STARTSPEED) - i * 10, 20, 10))
    for i in range(currentSpeed): # draw the white outlines
        pygame.draw.rect(DISPLAYSURF, WHITE, (15, 5 + (10 * STARTSPEED) - i * 10, 20, 10), 1)


def terminate():
    pygame.quit()
    sys.exit()




def getRandomVelocity():
    speed = random.randint(MINSPEED, MAXSPEED)
    if random.randint(0, 1) == 0:
        return speed
    else:
        return -speed


def getRandomOffCameraPos(camerax, cameray, objWidth, objHeight):
    # create a Rect of the camera view
    cameraRect = pygame.Rect(camerax, cameray, WINWIDTH, WINHEIGHT)
    while True:
        x = random.randint(camerax - WINWIDTH, camerax + (2 * WINWIDTH))
        y = random.randint(cameray - WINHEIGHT, cameray + (2 * WINHEIGHT))
        # create a Rect object with the random coordinates and use colliderect()
        # to make sure the right edge isn't in the camera view.
        objRect = pygame.Rect(x, y, objWidth, objHeight)
        if not objRect.colliderect(cameraRect):
            return x, y


def makeNewGarbage(camerax, cameray):
    ga = {}
    ga['surface'] = pygame.image.load('garbage.png');
    ga['width']  = 30
    ga['height'] = 30
    ga['x'], ga['y'] = getRandomOffCameraPos(camerax, cameray, ga['width'], ga['height'])
    ga['movex'] = getRandomVelocity()
    ga['movey'] = getRandomVelocity()
    if ga['movex'] < 0: # garbage is facing left
        ga['surface'] = pygame.transform.scale(GAR_IMG, (ga['width'], ga['height']))
    else: # garbage is facing right
        ga['surface'] = pygame.transform.scale(GAR_IMG, (ga['width'], ga['height']))
    
    return ga


def makeNewTreasure(camerax, cameray):
    tr = {}
    tr['surface'] = pygame.image.load('treasure.png');
    tr['width']  = 30
    tr['height'] = 30
    tr['x'], tr['y'] = getRandomOffCameraPos(camerax, cameray, tr['width'], tr['height'])
    tr['movex'] = getRandomVelocity()
    tr['movey'] = getRandomVelocity()
    if tr['movex'] < 0: # treasure is facing left
        tr['surface'] = pygame.transform.scale(TRE_IMG, (tr['width'], tr['height']))
    else: # treasure is facing right
        tr['surface'] = pygame.transform.scale(TRE_IMG, (tr['width'], tr['height']))
    
    return tr


def makeNewCleanup(camerax, cameray):
    cl = {}
    cl['surface'] = pygame.image.load('cleanup.png');
    cl['width']  = 30
    cl['height'] = 30
    cl['x'], cl['y'] = getRandomOffCameraPos(camerax, cameray, cl['width'], cl['height'])
    cl['movex'] = getRandomVelocity()
    cl['movey'] = getRandomVelocity()
    if cl['movex'] < 0: # cleanup is facing left
        cl['surface'] = pygame.transform.scale(CLE_IMG, (cl['width'], cl['height']))
    else: # cleanup is facing right
        cl['surface'] = pygame.transform.scale(CLE_IMG, (cl['width'], cl['height']))
    
    return cl


def isOutsideActiveArea(camerax, cameray, obj):
    # Return False if camerax and cameray are more than
    # a half-window length beyond the edge of the window.
    boundsLeftEdge = camerax - WINWIDTH
    boundsTopEdge = cameray - WINHEIGHT
    boundsRect = pygame.Rect(boundsLeftEdge, boundsTopEdge, WINWIDTH * 3, WINHEIGHT * 3)
    objRect = pygame.Rect(obj['x'], obj['y'], obj['width'], obj['height'])
    return not boundsRect.colliderect(objRect)




if __name__ == '__main__':
    main()
