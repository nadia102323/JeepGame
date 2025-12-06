#!/usr/bin/env python
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math, time, random, csv, datetime
import ImportObject
import PIL.Image as Image
import jeep, cone, star, diamond, ribbon, streetlamp

windowSize = 600
helpWindow = False
helpWin = 0
mainWin = 0
centered = False

isFullscreen = False
windowResolutions = [(600, 600), (800, 600), (1024, 768), (1280, 720), (1920, 1080)]
currentResolutionIndex = 0
normalWindowSize = windowResolutions[currentResolutionIndex]

beginTime = 0
countTime = 0
score = 0
finalScore = 0
canStart = False
overReason = ""
isLoading = True  # Add loading flag
loadingProgress = 0  # Track loading progress
totalLoadingSteps = 0  # Total number of loading steps
currentLoadingStep = 0  # Current step being processed
showHomeScreen = False  # Add home screen flag

#for wheel spinning
tickTime = 0

#creating objects
objectArray = []
jeep1Obj = jeep.jeep('p')
jeep2Obj = jeep.jeep('g')
jeep3Obj = jeep.jeep('r')

allJeeps = [jeep1Obj, jeep2Obj, jeep3Obj]
jeepNum = 0
jeepObj = allJeeps[jeepNum]

#personObj = person.person(10.0,10.0)

ribbonAmount = 3  # Number of acceleration ribbons on the track
allribbons = []
ribbonCoord = []
accelerationBoost = 2.0  # Speed multiplier when accelerated
accelerationDuration = 1000  # Duration in milliseconds
jeepAccelerated = False
accelerationEndTime = 0
normalMoveSpeed = 0.5
acceleratedMoveSpeed = normalMoveSpeed * accelerationBoost


# Object manipulation mode
manipulationMode = False  # Toggle between camera and object manipulation
selectedObject = None  # Will be set to starObj when in manipulation mode

#concerned with camera
eyeX = 0.0
eyeY = 2.0
eyeZ = 10.0
midDown = False
topView = False
behindView = False
frontView = False
zoomLevel = 1.0  # Add zoom level variable


#concerned with panning
nowX = 0.0
nowY = 0.0

angle = 0.0
radius = 10.0
phi = 0.0

#concerned with scene development
land = 20
gameEnlarge = 10

#concerned with obstacles (cones) & rewards (stars)
coneAmount = 15
starAmount = 5 #val = -10 pts
diamondAmount = 1 #val = deducts entire by 1/2
diamondObj = diamond.diamond(random.randint(-land, land), random.randint(10.0, land*gameEnlarge))
usedDiamond = False

allcones = []
allstars = []
obstacleCoord = []
rewardCoord = []
ckSense = 5.0

#concerned with lighting#########################!!!!!!!!!!!!!!!!##########
applyLighting = False
currentLightType = "none" 

fov = 30.0
attenuation = 1.0

light0_Position = [0.0, 1.0, 1.0, 1.0]
light0_Intensity = [0.75, 0.75, 0.75, 0.25]

light1_Position = [0.0, 0.0, 0.0, 0.0]
light1_Intensity = [0.25, 0.25, 0.25, 0.25]

matAmbient = [1.0, 1.0, 1.0, 1.0]
matDiffuse = [0.5, 0.5, 0.5, 1.0]
matSpecular = [0.5, 0.5, 0.5, 1.0]
matShininess  = 100.0

lampAmount = 8  # Number of street lamps
alllamps = []
lampSpacing = (land * gameEnlarge) / lampAmount  # Even spacing along the road
lampOffset = 3  # Distance from road edge to lamp position


#--------------------------------------developing scene---------------
class Scene:
    axisColor = (0.5, 0.5, 0.5, 0.5)
    axisLength = 50   # Extends to positive and negative on all axes
    landColor = (.47, .53, .6, 0.5) #Light Slate Grey
    landLength = land  # Extends to positive and negative on x and y axis
    landW = 1.0
    landH = 0.0
    cont = gameEnlarge
    grassExtend = 30
    
    def draw(self):
        self.drawAxis()
        self.drawGrass()
        self.drawLand()

    def drawAxis(self):
        glColor4f(self.axisColor[0], self.axisColor[1], self.axisColor[2], self.axisColor[3])
        glBegin(GL_LINES)
        glVertex(-self.axisLength, 0, 0)
        glVertex(self.axisLength, 0, 0)
        glVertex(0, -self.axisLength, 0)
        glVertex(0, self.axisLength, 0)
        glVertex(0, 0, -self.axisLength)
        glVertex(0, 0, self.axisLength)
        glEnd()

    def drawGrass(self):
        """Draw grass texture on both sides of the road"""
        glEnable(GL_TEXTURE_2D)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
        glBindTexture(GL_TEXTURE_2D, grassTextureID)

        # Left grass area
        glBegin(GL_POLYGON)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-self.landLength - self.grassExtend, -0.1, self.cont * self.landLength)
        glTexCoord2f(0.0, 5.0)
        glVertex3f(-self.landLength - self.grassExtend, -0.1, -self.landLength)
        glTexCoord2f(2.0, 5.0)
        glVertex3f(-self.landLength, -0.1, -self.landLength)
        glTexCoord2f(2.0, 0.0)
        glVertex3f(-self.landLength, -0.1, self.cont * self.landLength)
        glEnd()

        # Right grass area
        glBegin(GL_POLYGON)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(self.landLength, -0.1, self.cont * self.landLength)
        glTexCoord2f(0.0, 5.0)
        glVertex3f(self.landLength, -0.1, -self.landLength)
        glTexCoord2f(2.0, 5.0)
        glVertex3f(self.landLength + self.grassExtend, -0.1, -self.landLength)
        glTexCoord2f(2.0, 0.0)
        glVertex3f(self.landLength + self.grassExtend, -0.1, self.cont * self.landLength)
        glEnd()

        # Front grass area (before starting line)
        glBegin(GL_POLYGON)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-self.landLength - self.grassExtend, -0.1, -self.landLength)
        glTexCoord2f(0.0, 2.0)
        glVertex3f(-self.landLength - self.grassExtend, -0.1, -self.landLength - self.grassExtend)
        glTexCoord2f(5.0, 2.0)
        glVertex3f(self.landLength + self.grassExtend, -0.1, -self.landLength - self.grassExtend)
        glTexCoord2f(5.0, 0.0)
        glVertex3f(self.landLength + self.grassExtend, -0.1, -self.landLength)
        glEnd()

        # Back grass area (after finish line)
        glBegin(GL_POLYGON)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-self.landLength - self.grassExtend, -0.1, self.cont * self.landLength)
        glTexCoord2f(0.0, 2.0)
        glVertex3f(-self.landLength - self.grassExtend, -0.1, self.cont * self.landLength + self.grassExtend)
        glTexCoord2f(5.0, 2.0)
        glVertex3f(self.landLength + self.grassExtend, -0.1, self.cont * self.landLength + self.grassExtend)
        glTexCoord2f(5.0, 0.0)
        glVertex3f(self.landLength + self.grassExtend, -0.1, self.cont * self.landLength)
        glEnd()

        glDisable(GL_TEXTURE_2D)


    def drawLand(self):
        glEnable(GL_TEXTURE_2D)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
        glBindTexture(GL_TEXTURE_2D, roadTextureID)

        glBegin(GL_POLYGON)

        glTexCoord2f(self.landH, self.landH)
        glVertex3f(self.landLength, 0, self.cont * self.landLength)

        glTexCoord2f(self.landH, self.landW)
        glVertex3f(self.landLength, 0, -self.landLength)

        glTexCoord2f(self.landW, self.landW)
        glVertex3f(-self.landLength, 0, -self.landLength)

        glTexCoord2f(self.landW, self.landH)
        glVertex3f(-self.landLength, 0, self.cont * self.landLength)
        glEnd()

        glDisable(GL_TEXTURE_2D)

#--------------------------------------populating scene----------------
def staticObjects():
    global objectArray
    objectArray.append(Scene())
    print ('append')


def updateLoadingProgress(stepName=""):
    """Update loading progress and display"""
    global currentLoadingStep, loadingProgress
    currentLoadingStep += 1
    loadingProgress = int((currentLoadingStep / totalLoadingSteps) * 100)
    if stepName:
        print(f"Loading: {stepName} ({loadingProgress}%)")
    
    # Force immediate display update
    display()
    
    # Process events to allow display to refresh
    glutMainLoopEvent()

def display():
    global jeepObj, canStart, score, beginTime, countTime, jeepAccelerated, isLoading, loadingProgress, showHomeScreen
    
    # Show loading screen with progress text only
    if isLoading:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glDisable(GL_LIGHTING)
        
        # Set up orthographic projection for 2D rendering
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, windowSize, 0, windowSize)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Draw "Loading..." text (centered)
        glColor3f(1.0, 1.0, 1.0)
        loadingText = f"Loading... {loadingProgress}%"
        textWidth = len(loadingText) * 9  # Approximate pixel width per character
        textX = (windowSize - textWidth) / 2
        textY = windowSize / 2  # Centered vertically
        glRasterPos2f(textX, textY)
        for char in loadingText:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
        
        # Restore projection matrix
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        
        glutSwapBuffers()
        return
    
    # Show home screen
    if showHomeScreen:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glDisable(GL_LIGHTING)
        
        # Set up orthographic projection for 2D rendering
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, windowSize, 0, windowSize)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Draw game title
        glColor3f(0.0, 1.0, 1.0)
        titleText = "JEEP GAME"
        titleWidth = len(titleText) * 13  # Approximate width for larger font
        titleX = (windowSize - titleWidth) / 2
        titleY = windowSize / 2 + 50
        glRasterPos2f(titleX, titleY)
        for char in titleText:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))
        
        # Draw "Press SPACE to Start" text (blinking effect)
        blinkTime = int(glutGet(GLUT_ELAPSED_TIME) / 500) % 2  # Blink every 500ms
        if blinkTime == 0:
            glColor3f(1.0, 1.0, 0.0)
            startText = "Press SPACE to Start"
            startWidth = len(startText) * 9
            startX = (windowSize - startWidth) / 2
            startY = windowSize / 2 - 50
            glRasterPos2f(startX, startY)
            for char in startText:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
        
        # Restore projection matrix
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        
        glutSwapBuffers()
        glutPostRedisplay()  # Keep updating for blinking effect
        return
    
    if not topView and not frontView and not behindView:
        setObjView()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Apply lighting based on menu selection
    if applyLighting == True and currentLightType != "none":
        # Set material properties for objects
        glMaterialfv(GL_FRONT, GL_AMBIENT, matAmbient)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, matDiffuse)
        glMaterialfv(GL_FRONT, GL_SPECULAR, matSpecular)
        glMaterialfv(GL_FRONT, GL_SHININESS, matShininess)
        
        # Update spotlight position dynamically if spotlight is active
        if currentLightType == "spotlight":
            spotlight_pos = [jeepObj.posX, jeepObj.posY + 10.0, jeepObj.posZ, 1.0]
            glLightfv(GL_LIGHT0, GL_POSITION, spotlight_pos)
        
        # Visualize light source for point lights and spotlights
        if currentLightType in ["point", "spotlight"]:
            # Temporarily disable lighting to draw light source indicator
            glDisable(GL_LIGHTING)
            glColor3f(1.0, 1.0, 0.0)  # Yellow sphere for light source
            glPushMatrix()
            
            if currentLightType == "point":
                glTranslatef(light0_Position[0], light0_Position[1], light0_Position[2])
            else:  # spotlight
                glTranslatef(jeepObj.posX, jeepObj.posY + 10.0, jeepObj.posZ)
            
            glutSolidSphere(0.5, 16, 12)
            glPopMatrix()
            
            # Re-enable lighting
            glEnable(GL_LIGHTING)
    
    # Display current lighting type on screen
    glDisable(GL_LIGHTING)  # Temporarily disable for text rendering
    glColor3f(1.0, 1.0, 1.0)
    text3d(f"Lighting: {currentLightType.title()}", -18, 8, 0)

    # Re-enable lighting if it should be active
    if applyLighting == True and currentLightType != "none":
        glEnable(GL_LIGHTING)
   
    beginTime = 6-score
    countTime = score-6
    if (score <= 5):
        canStart = False
        glDisable(GL_LIGHTING)  # Disable for text
        glColor3f(1.0,0.0,1.0)
        text3d("Begins in: "+str(beginTime), jeepObj.posX, jeepObj.posY + 3.0, jeepObj.posZ)
        if applyLighting and currentLightType != "none":
            glEnable(GL_LIGHTING)
    elif (score == 6):
        canStart = True
        glDisable(GL_LIGHTING)  # Disable for text
        glColor3f(1.0,0.0,1.0)
        text3d("GO!", jeepObj.posX, jeepObj.posY + 3.0, jeepObj.posZ)
        if applyLighting and currentLightType != "none":
            glEnable(GL_LIGHTING)
    else:
        canStart = True
        glDisable(GL_LIGHTING)  # Disable for text
        glColor3f(0.0,1.0,1.0)
        text3d("Scoring: "+str(countTime), jeepObj.posX, jeepObj.posY + 3.0, jeepObj.posZ)
        if applyLighting and currentLightType != "none":
            glEnable(GL_LIGHTING)

    for obj in objectArray:
        obj.draw()
    for cone in allcones:
        cone.draw()
    for starObj in allstars:
        starObj.draw()
    for ribbonObj in allribbons:
        ribbonObj.draw()
    for lampObj in alllamps:
        lampObj.draw()

    if (usedDiamond == False):
        diamondObj.draw()
    
    jeepObj.draw()
    jeepObj.drawW1()
    jeepObj.drawW2()
    jeepObj.drawLight()
    #personObj.draw()
    
    # Only draw allstars if they exist
    for starObj in allstars:
        starObj.draw()
    
    glutSwapBuffers()

def idle():#--------------with more complex display items like turning wheel---
    global tickTime, prevTime, score, jeepAccelerated, accelerationEndTime
    jeepObj.rotateWheel(-0.1 * tickTime)    
    
    # Check if acceleration has expired
    curTime = glutGet(GLUT_ELAPSED_TIME)
    if jeepAccelerated and curTime > accelerationEndTime:
        jeepAccelerated = False
        print("Acceleration ended - returning to normal speed")
    
    # Update automatic objects
    updateAutomaticObjects()
    
    glutPostRedisplay()
    
    tickTime = curTime - prevTime
    prevTime = curTime
    score = curTime/1000
    

#---------------------------------setting camera----------------------------
def setView():
    global eyeX, eyeY, eyeZ
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    
    # Calculate aspect ratio from current window size
    width = glutGet(GLUT_WINDOW_WIDTH)
    height = glutGet(GLUT_WINDOW_HEIGHT)
    aspectRatio = width / height if height != 0 else 1.0
    
    # Apply zoom
    baseFov = 90.0
    currentFov = baseFov / zoomLevel
    currentFov = max(10, min(150, currentFov))
    
    gluPerspective(currentFov, aspectRatio, 0.1, 100)
    
    if (topView == True):
        cameraHeight = 30.0  # Much higher than before
        gluLookAt(jeepObj.posX, cameraHeight, jeepObj.posZ,  # Camera position above jeep
                  jeepObj.posX, jeepObj.posY, jeepObj.posZ,  # Look at jeep
                  0, 0, 1)         
        print("top view")
    elif (frontView ==True):
        gluLookAt(eyeX, eyeY, eyeZ, 0, 0, 0, 0, 1, 0)
        print("front view")
    else:
        #gluLookAt(jeepObj.posX, jeepObj.posY + 10.0, jeepObj.posZ - 20.0, jeepObj.posX, jeepObj.posY, jeepObj.posZ, 0, 1, 0) 
        #print("default view")
        setObjView()
        return
    glMatrixMode(GL_MODELVIEW)
    glutPostRedisplay()
    

def setObjView():
    # things to do
    # realize a view following the jeep
    # refer to setview
    global eyeX, eyeY, eyeZ
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    
    # Apply zoom by adjusting field of view
    baseFov = 90.0
    currentFov = baseFov / zoomLevel
    currentFov = max(10, min(150, currentFov))
    
    # Calculate aspect ratio from current window size
    width = glutGet(GLUT_WINDOW_WIDTH)
    height = glutGet(GLUT_WINDOW_HEIGHT)
    aspectRatio = width / height if height != 0 else 1.0
    
    gluPerspective(currentFov, aspectRatio, 0.1, 100)
    
    # Camera follows the jeep from behind and slightly above
    cameraDistance = 20.0
    cameraHeight = 10.0
    
    # Position camera behind the jeep
    cameraX = jeepObj.posX
    cameraY = jeepObj.posY + cameraHeight
    cameraZ = jeepObj.posZ - cameraDistance
    
    # Look at the jeep
    gluLookAt(cameraX, cameraY, cameraZ,  # Camera position
              jeepObj.posX, jeepObj.posY, jeepObj.posZ,  # Look at jeep
              0, 1, 0)  # Up vector
    
    glMatrixMode(GL_MODELVIEW)
    #glutPostRedisplay()

#-------------------------------------------user inputs------------------
def mouseHandle(button, state, x, y):
    global midDown
    if (button == GLUT_MIDDLE_BUTTON and state == GLUT_DOWN):
        midDown = True
        print ('pushed')
    else:
        midDown = False    


def motionHandle(x,y):
    global nowX, nowY, angle, eyeX, eyeY, eyeZ, phi
    if (midDown == True):
        pastX = nowX
        pastY = nowY 
        nowX = x
        nowY = y
        if (nowX - pastX > 0):
            angle -= 0.25
        elif (nowX - pastX < 0):
            angle += 0.25
        #elif (nowY - pastY > 0): look into looking over and under object...
            #phi += 1.0
        #elif (nowX - pastY <0):
            #phi -= 1.0
        eyeX = radius * math.sin(angle) 
        eyeZ = radius * math.cos(angle)
        #eyeY = radius * math.sin(phi)
    if centered == False:
        setView()
    elif centered == True:
        setObjView()
    #print eyeX, eyeY, eyeZ, nowX, nowY, radius, angle
    #print "getting handled"

def mouseWheelHandle(wheel, direction, x, y):
    global zoomLevel
    zoomFactor = 1.1
    
    if direction < 0:  # Scroll up - zoom in
        zoomLevel /= zoomFactor
        print(f"Zooming in - zoom level: {zoomLevel:.2f}")
    else:  # Scroll down - zoom out
        zoomLevel *= zoomFactor
        print(f"Zooming out - zoom level: {zoomLevel:.2f}")
    
    # Clamp zoom level to reasonable bounds
    zoomLevel = max(0.1, min(5.0, zoomLevel))
    
    setView()

    
def specialKeys(keypress, mX, mY):
    # things to do
    # this is the function to move the car
    global canStart, jeepAccelerated
    if not canStart:
        return
    
    # Use different move speeds based on acceleration status
    moveSpeed = acceleratedMoveSpeed if jeepAccelerated else normalMoveSpeed

    if keypress == GLUT_KEY_UP:
        print("Arrow Up - moving forward")
        jeepObj.posZ += moveSpeed
        collisionCheck()
        glutPostRedisplay()
    elif keypress == GLUT_KEY_DOWN:
        print("Arrow Down - moving backward")
        jeepObj.posZ -= moveSpeed
        collisionCheck()
    elif keypress == GLUT_KEY_LEFT:
        print("Arrow Left - moving left")
        jeepObj.posX += moveSpeed
        collisionCheck()
    elif keypress == GLUT_KEY_RIGHT:
        print("Arrow Right - moving right")
        jeepObj.posX -= moveSpeed
        collisionCheck()
    
    glutPostRedisplay()

    pass

def myKeyboard(key, mX, mY):
    global eyeX, eyeY, eyeZ, angle, radius, helpWindow, centered, helpWin, overReason, topView, behindView, frontView, isFullscreen, jeepAccelerated, showHomeScreen
    
    # Handle space key to start game from home screen
    if key == b' ' and showHomeScreen:
        showHomeScreen = False
        print("Starting game!")
        glutPostRedisplay()
        return
    
    if key == b"h":
        print ("h pushed"+ str(helpWindow))
        winNum = glutGetWindow()
        if helpWindow == False:
            helpWindow = True
            glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
            glutInitWindowSize(500,300)
            glutInitWindowPosition(600,0)
            helpWin = glutCreateWindow(b'Help Guide')
            glutDisplayFunc(showHelp)
            glutKeyboardFunc(myKeyboard)
            glutMainLoop()
        elif helpWindow == True and winNum!=1:
            helpWindow = False
            print (glutGetWindow())
            glutHideWindow()
            #glutDestroyWindow(helpWin)
            glutMainLoop()

    # things can do
    # this is the part to set special functions, such as help window.

    elif key == b'5':
        print("5 pushed")
        topView = not topView
        behindView, frontView = False, False
        setView()
    elif key == b'2':
        print("2 pushed")
        behindView = not behindView
        topView, frontView = False, False
        setView()
    elif key == b'8':
        print("8 pushed")
        frontView = not frontView
        behindView, topView = False, False
        setView()
   
    elif key == b'w':
        print("w pushed")
        if canStart:
            moveSpeed = acceleratedMoveSpeed if jeepAccelerated else normalMoveSpeed
            jeepObj.posZ += moveSpeed
            collisionCheck()
            glutPostRedisplay()
    elif key == b's':
        print("s pushed")
        if canStart:
            moveSpeed = acceleratedMoveSpeed if jeepAccelerated else normalMoveSpeed
            jeepObj.posZ -= moveSpeed
            collisionCheck()
            glutPostRedisplay()
    elif key == b'a':
        print("a pushed")
        if canStart:
            moveSpeed = acceleratedMoveSpeed if jeepAccelerated else normalMoveSpeed
            jeepObj.posX += moveSpeed
            collisionCheck()
            glutPostRedisplay()
    elif key == b'd':
        print("d pushed")
        if canStart:
            moveSpeed = acceleratedMoveSpeed if jeepAccelerated else normalMoveSpeed
            jeepObj.posX -= moveSpeed
            collisionCheck()
            glutPostRedisplay()

    elif key == b'f' or key == b'F':
        print("f pushed - toggling fullscreen")
        toggleFullscreen()


#-------------------------------------------------tools----------------------       
def drawTextBitmap(string, x, y): #for writing text to display
    glRasterPos2f(x, y)
    for char in string:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

def text3d(string, x, y, z):
    glRasterPos3f(x,y,z)
    for char in string:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

def dist(pt1, pt2):
    a = pt1[0]
    b = pt1[1]
    x = pt2[0]
    y = pt2[1]
    return math.sqrt((a-x)**2 + (b-y)**2)

def noReshape(newX, newY): #used to ensure program works correctly when resized
    global windowSize, normalWindowSize, isFullscreen
    
    # Get screen dimensions
    screenWidth = glutGet(GLUT_SCREEN_WIDTH)
    screenHeight = glutGet(GLUT_SCREEN_HEIGHT)
    
    # Check if window is being maximized (within 10 pixels of screen size)
    if not isFullscreen and abs(newX - screenWidth) < 10 and abs(newY - screenHeight) < 10:
        print("Window maximized - entering fullscreen")
        toggleFullscreen()
        return
    
    if not isFullscreen:
        # Allow window to be resized
        windowSize = min(newX, newY)
        normalWindowSize = (newX, newY)
        
        # Update viewport
        glViewport(0, 0, newX, newY)
        
        # Update projection matrix with new aspect ratio
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        aspectRatio = newX / newY if newY != 0 else 1.0
        baseFov = 90.0
        currentFov = baseFov / zoomLevel
        currentFov = max(10, min(150, currentFov))
        
        gluPerspective(currentFov, aspectRatio, 0.1, 100)
        glMatrixMode(GL_MODELVIEW)
        
        print(f"Window resized to: {newX}x{newY}, aspect ratio: {aspectRatio:.2f}")
        glutPostRedisplay()
    else:
        # In fullscreen mode, update viewport to match screen size
        glViewport(0, 0, newX, newY)
        glutPostRedisplay()


def toggleFullscreen():
    global isFullscreen, normalWindowSize
    if isFullscreen:
        # Exit fullscreen
        glutReshapeWindow(normalWindowSize[0], normalWindowSize[1])
        glutPositionWindow(50, 50)
        isFullscreen = False
        print(f"Exiting fullscreen - restoring window to {normalWindowSize[0]}x{normalWindowSize[1]}")
        
        # Update the view after exiting fullscreen
        if topView or frontView or behindView:
            setView()
        else:
            setObjView()
    else:
        # Save current window size before going fullscreen
        normalWindowSize = (glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT))
        
        # Enter fullscreen
        glutFullScreen()
        isFullscreen = True
        print("Entering fullscreen")
        
        # Update the view after entering fullscreen
        if topView or frontView or behindView:
            setView()
        else:
            setObjView()
    
    glutPostRedisplay()



#--------------------------------------------making game more complex--------
def addCone(x,z, automatic=False):
    #allcones.append(cone.cone(x,z))
    #obstacleCoord.append((x,z))
    newCone = cone.cone(x, z)
    newCone.isAutomatic = automatic
    allcones.append(newCone)
    obstacleCoord.append((x, z))

def updateAutomaticObjects():
    """Update all automatic objects"""
    global obstacleCoord
    
    for i, coneObj in enumerate(allcones):
        if hasattr(coneObj, 'isAutomatic') and coneObj.isAutomatic:
            oldX = coneObj.posX
            coneObj.update(land, jeepObj, allcones)
            
            # Update obstacle coordinates for collision detection
            if i < len(obstacleCoord):
                obstacleCoord[i] = (coneObj.posX, coneObj.posZ)


def collisionCheck():

    global overReason, score, usedDiamond, countTime, jeepAccelerated, accelerationEndTime
    for obstacle in obstacleCoord:
        if dist((jeepObj.posX, jeepObj.posZ), obstacle) <= ckSense:
            overReason = "You hit an obstacle!"
            gameOver()
    if (jeepObj.posX >= land or jeepObj.posX <= -land):
        overReason = "You ran off the road!"
        gameOver()

    # Check for ribbon collision (acceleration boost)
    for i, ribbonPos in enumerate(ribbonCoord):
        if dist((jeepObj.posX, jeepObj.posZ), ribbonPos) <= ckSense:
            if not jeepAccelerated:  # Only activate if not already accelerated
                print("Acceleration ribbon activated!")
                jeepAccelerated = True
                curTime = glutGet(GLUT_ELAPSED_TIME)
                accelerationEndTime = curTime + accelerationDuration
                # Remove the ribbon after use
                ribbonCoord.pop(i)
                allribbons.pop(i)
                break

    if (dist((jeepObj.posX, jeepObj.posZ), (diamondObj.posX, diamondObj.posZ)) <= ckSense and usedDiamond ==False):
        print ("Diamond bonus!")
        countTime /= 2
        usedDiamond = True
    if (jeepObj.posZ >= land*gameEnlarge):
        gameSuccess()

    """global overReason, score, usedDiamond, countTime, jeepAccelerated, accelerationEndTime
    for obstacle in obstacleCoord:
        if dist((jeepObj.posX, jeepObj.posZ), obstacle) <= ckSense:
            overReason = "You hit an obstacle!"
            gameOver()
    if (jeepObj.posX >= land or jeepObj.posX <= -land):
        overReason = "You ran off the road!"
        gameOver()

    # Check for ribbon collision (acceleration boost)
    for i, ribbon in enumerate(ribbonCoord):
        if dist((jeepObj.posX, jeepObj.posZ), ribbon) <= ckSense:
            if not jeepAccelerated:  # Only activate if not already accelerated
                print("Acceleration ribbon activated!")
                jeepAccelerated = True
                curTime = glutGet(GLUT_ELAPSED_TIME)
                accelerationEndTime = curTime + accelerationDuration
                # Remove the ribbon after use (optional)
                ribbonCoord.pop(i)
                allribbons.pop(i)
                break

    if (dist((jeepObj.posX, jeepObj.posZ), (diamondObj.posX, diamondObj.posZ)) <= ckSense and usedDiamond ==False):
        print ("Diamond bonus!")
        countTime /= 2
        usedDiamond = True
    if (jeepObj.posZ >= land*gameEnlarge):
        gameSuccess()
    """
#----------------------------------multiplayer dev (using tracker)-----------
def recordGame():
    with open('results.csv', 'wt') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        print(st)
        spamwriter.writerow([st] + [finalScore])
    
#-------------------------------------developing additional windows/options----
def gameOver():
    global finalScore
    print ("Game completed!")
    finalScore = score-6
    #recordGame() #add to excel
    glutHideWindow()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    glutInitWindowSize(200,200)
    glutInitWindowPosition(600,100)
    overWin = glutCreateWindow("Game Over!")
    glutDisplayFunc(overScreen)
    glutMainLoop()
    
def gameSuccess():
    global finalScore
    print ("Game success!")
    finalScore = score-6
    #recordGame() #add to excel
    glutHideWindow()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    glutInitWindowSize(200,200)
    glutInitWindowPosition(600,100)
    overWin = glutCreateWindow("Complete!")
    glutDisplayFunc(winScreen)
    glutMainLoop()

def winScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glColor3f(0.0,1.0,0.0)
    drawTextBitmap("Completed Trial!" , -0.6, 0.85)
    glColor3f(0.0,1.0,0.0)
    drawTextBitmap("Your score is: ", -1.0, 0.0)
    glColor3f(1.0,1.0,1.0)
    drawTextBitmap(str(finalScore), -1.0, -0.15)
    glutSwapBuffers()


def overScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glColor3f(1.0,0.0,1.0)
    drawTextBitmap("Incomplete Trial" , -0.6, 0.85)
    glColor3f(0.0,1.0,0.0)
    drawTextBitmap("Because you..." , -1.0, 0.5)
    glColor3f(1.0,1.0,1.0)
    drawTextBitmap(overReason, -1.0, 0.35)
    glColor3f(0.0,1.0,0.0)
    drawTextBitmap("Your score stopped at: ", -1.0, 0.0)
    glColor3f(1.0,1.0,1.0)
    drawTextBitmap(str(finalScore), -1.0, -0.15)
    glutSwapBuffers()

def showHelp():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glColor3f(1.0,0.0,0.0)
    drawTextBitmap("Help Guide" , -0.2, 0.85)
    glColor3f(0.0,0.0,1.0)
    drawTextBitmap("1. Move the jeep using arrow keys / WASD keys" , -1.0, 0.7)
    drawTextBitmap("2. Zoom in and out by mouse scroll wheel" , -1.0, 0.55)
    drawTextBitmap("3. Toggle views using keys: 5 (top), 2 (behind), 8 (front)" , -1.0, 0.4)
    drawTextBitmap("4. Press H to show/hide this help window" , -1.0, 0.25)
    drawTextBitmap("5. Press R to cycle resolution" , -1.0, 0.1)
    #drawTextBitmap("6. Press F to toggle fullscreen" , -1.0, -0.05)
    drawTextBitmap("6. Right-click to change lighting options" , -1.0, -0.05)
    glutSwapBuffers()


#----------------------------------------------texture development-----------
def loadTexture(imageName):
    texturedImage = Image.open(imageName)
    try:
        imgX = texturedImage.size[0]
        imgY = texturedImage.size[1]
        img = texturedImage.tobytes("raw","RGBX",0,-1)#tostring("raw", "RGBX", 0, -1)
    except Exception:
        print ("Error:")
        print ("Switching to RGBA mode.")
        imgX = texturedImage.size[0]
        imgY = texturedImage.size[1]
        img = texturedImage.tobytes("raw","RGB",0,-1)#tostring("raw", "RGBA", 0, -1)

    tempID = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tempID)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_MIRRORED_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_MIRRORED_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexImage2D(GL_TEXTURE_2D, 0, 3, imgX, imgY, 0, GL_RGBA, GL_UNSIGNED_BYTE, img)
    return tempID

def loadSceneTextures():
    global roadTextureID, grassTextureID
    roadTextureID = loadTexture('../img/road2.png')
    grassTextureID = loadTexture('../img/grass.png')

#-----------------------------------------------lighting work--------------
def initializeLight():
    glEnable(GL_LIGHTING)                
    glEnable(GL_LIGHT0)                 
    glEnable(GL_DEPTH_TEST)              
    glEnable(GL_NORMALIZE)               
    glClearColor(0.1, 0.1, 0.1, 0.0)

def setupAmbientLight():
    resetLightingState()
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    
    # Strong ambient component, weak diffuse/specular
    ambient = [0.8, 0.8, 0.8, 1.0]
    diffuse = [0.2, 0.2, 0.2, 1.0]
    specular = [0.1, 0.1, 0.1, 1.0]
    
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, specular)
    glLightfv(GL_LIGHT0, GL_POSITION, light0_Position)

def setupPointLight():
    resetLightingState()
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    
    # Standard point light properties
    ambient = [0.2, 0.2, 0.2, 1.0]
    diffuse = [0.8, 0.8, 0.8, 1.0]
    specular = [1.0, 1.0, 1.0, 1.0]
    
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, specular)
    glLightfv(GL_LIGHT0, GL_POSITION, light0_Position)
    
    # Set attenuation for point light
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 1.0)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.1)
    glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, 0.01)

def setupDirectionalLight():
    resetLightingState()
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    
    # Directional light position (w=0 makes it directional)
    directional_pos = [1.0, 1.0, 0.5, 0.0]
    
    ambient = [0.3, 0.3, 0.3, 1.0]
    diffuse = [0.7, 0.7, 0.7, 1.0]
    specular = [0.5, 0.5, 0.5, 1.0]
    
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, specular)
    glLightfv(GL_LIGHT0, GL_POSITION, directional_pos)

def setupSpotlight():
    resetLightingState()
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    
    # Spotlight position above jeep
    spotlight_pos = [jeepObj.posX, jeepObj.posY + 10.0, jeepObj.posZ, 1.0]
    spotlight_dir = [0.0, -1.0, 0.0]  # Points downward
    
    ambient = [0.1, 0.1, 0.1, 1.0]
    diffuse = [1.0, 1.0, 1.0, 1.0]
    specular = [1.0, 1.0, 1.0, 1.0]
    
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, specular)
    glLightfv(GL_LIGHT0, GL_POSITION, spotlight_pos)
    
    # Spotlight specific properties
    glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, spotlight_dir)
    glLightf(GL_LIGHT0, GL_SPOT_CUTOFF, 30.0)  # 30 degree cone
    glLightf(GL_LIGHT0, GL_SPOT_EXPONENT, 2.0)  # Focus
    
    # Attenuation
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 1.0)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
    glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, 0.005)


def resetLightingState():
    """Completely reset all lighting state to OpenGL defaults"""
    # Disable all lighting first
    glDisable(GL_LIGHTING)
    glDisable(GL_LIGHT0)
    glDisable(GL_LIGHT1)
    
    # Reset all light properties to OpenGL defaults
    default_ambient = [0.0, 0.0, 0.0, 1.0]
    default_diffuse = [1.0, 1.0, 1.0, 1.0]
    default_specular = [1.0, 1.0, 1.0, 1.0]
    default_position = [0.0, 0.0, 1.0, 0.0]
    default_spot_direction = [0.0, 0.0, -1.0]
    
    glLightfv(GL_LIGHT0, GL_AMBIENT, default_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, default_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, default_specular)
    glLightfv(GL_LIGHT0, GL_POSITION, default_position)
    
    # Reset spotlight properties
    glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, default_spot_direction)
    glLightf(GL_LIGHT0, GL_SPOT_CUTOFF, 180.0)  # 180 = no spotlight
    glLightf(GL_LIGHT0, GL_SPOT_EXPONENT, 0.0)
    
    # Reset attenuation to defaults
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 1.0)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.0)
    glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, 0.0)
    
    # Reset clear color to original black
    glClearColor(0.0, 0.0, 0.0, 0.0)


#-----------------------------------------------menu----------------------------------
def myMenu(option):
    global applyLighting, currentLightType
    
    if option == 1:
        applyLighting = True
        currentLightType = "ambient"
        setupAmbientLight()
        print("ambient")
    elif option == 2:
        applyLighting = True
        currentLightType = "point"
        setupPointLight()
        print("point")
    elif option == 3:
        applyLighting = True
        currentLightType = "directional"
        setupDirectionalLight()
        print("directional")
    elif option == 4:
        applyLighting = True
        currentLightType = "spotlight"
        setupSpotlight()
        print("spotlight")
    elif option == 5:
        applyLighting = False
        currentLightType = "none"
        # Reset to original clear color
        resetLightingState()
        print("Reset")

    print("Current Light Type: " + currentLightType)
    glutPostRedisplay()

#~~~~~~~~~~~~~~~~~~~~~~~~~the finale!!!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def finishLoading():
    """Called when all objects are loaded"""
    global isLoading, showHomeScreen
    isLoading = False
    showHomeScreen = True  # Show home screen after loading
    print("All objects loaded! Showing home screen.")
    glutPostRedisplay()

    
def main():
    glutInit()

    global prevTime, mainWin, loadingProgress, isLoading, totalLoadingSteps, currentLoadingStep
    prevTime = glutGet(GLUT_ELAPSED_TIME)
    
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    glutInitWindowSize(windowSize, windowSize)
    glutInitWindowPosition(0, 0)
    mainWin = glutCreateWindow(b'CS4182')
    glutDisplayFunc(display)
    glutIdleFunc(idle)

    setView()
    glLoadIdentity()
    glEnable(GL_DEPTH_TEST)   

    glutMouseFunc(mouseHandle)
    glutMotionFunc(motionHandle)
    glutMouseWheelFunc(mouseWheelHandle)
    glutSpecialFunc(specialKeys)
    glutKeyboardFunc(myKeyboard)
    glutReshapeFunc(noReshape)
    
    glutCreateMenu(myMenu)
    glutAddMenuEntry("Ambient Light", 1)
    glutAddMenuEntry("Point Light", 2)
    glutAddMenuEntry("Directional Light", 3)
    glutAddMenuEntry("Spotlight", 4)
    glutAddMenuEntry("No Lighting", 5)
    glutAttachMenu(GLUT_RIGHT_BUTTON)

    # Calculate total loading steps
    totalLoadingSteps = (
        1 +  # Load textures
        3 +  # Load jeep models (3 jeeps)
        (coneAmount - 2) +  # Create regular cones
        2 +  # Create automatic cones
        (coneAmount) +  # Make cone display lists
        starAmount +  # Create stars
        starAmount +  # Make star display lists
        1 +  # Create diamond
        ribbonAmount * 2 +  # Create and setup ribbons
        (lampAmount * 2) +  # Create street lamps
        1 +  # Create static objects
        1   # Initialize lighting
    )
    
    print(f"Total loading steps: {totalLoadingSteps}")
    
    currentLoadingStep = 0
    loadingProgress = 0
    isLoading = True

    # Show initial loading screen
    display()
    # filepath: c:\Users\NADIA\CS4182\project\src\main.py
    glutSwapBuffers()
    glutMainLoopEvent()
    
    # Add small delay to ensure window is fully initialized
    import time
    time.sleep(0.1)

    # Load textures
    updateLoadingProgress("Loading textures")
    loadSceneTextures()

    # Load jeep models
    updateLoadingProgress("Loading jeep 1")
    jeep1Obj.makeDisplayLists()
    
    updateLoadingProgress("Loading jeep 2")
    jeep2Obj.makeDisplayLists()
    
    updateLoadingProgress("Loading jeep 3")
    jeep3Obj.makeDisplayLists()

    # Create cones
    for i in range(coneAmount - 2):
        updateLoadingProgress(f"Creating obstacle {i+1}/{coneAmount-2}")
        addCone(random.randint(-land, land), random.randint(10.0, land*gameEnlarge))
    
    updateLoadingProgress("Creating automatic obstacle 1")
    addCone(random.randint(-land//2, land//2), random.randint(20.0, 40.0), automatic=True)
    
    updateLoadingProgress("Creating automatic obstacle 2")
    addCone(random.randint(-land//2, land//2), random.randint(60.0, 80.0), automatic=True)

    # Make cone display lists
    for i, cone in enumerate(allcones):
        updateLoadingProgress(f"Processing obstacle {i+1}/{len(allcones)}")
        cone.makeDisplayLists()

    # Create stars
    for i in range(starAmount):
        updateLoadingProgress(f"Creating reward {i+1}/{starAmount}")
        newStarX = random.randint(-land, land)
        newStarZ = random.randint(10.0, land*gameEnlarge)
        allstars.append(star.star(newStarX, newStarZ))
        rewardCoord.append((newStarX, newStarZ))

    # Make star display lists
    for i, starObj in enumerate(allstars):
        updateLoadingProgress(f"Processing reward {i+1}/{len(allstars)}")
        starObj.makeDisplayLists()

    # Create diamond
    updateLoadingProgress("Creating special item")
    diamondObj.makeDisplayLists()

    # Create ribbons
    for i in range(ribbonAmount):
        updateLoadingProgress(f"Creating acceleration ribbon {i+1}/{ribbonAmount}")
        newRibbonX = random.randint(-land//2, land//2)
        newRibbonZ = random.randint(30.0, land*gameEnlarge - 30.0)
        newRibbon = ribbon.ribbon(newRibbonX, newRibbonZ)
        
        updateLoadingProgress(f"Loading ribbon texture {i+1}/{ribbonAmount}")
        newRibbon.loadTexture('../img/accelerating_ribbon.png')
        newRibbon.makeDisplayLists()
        allribbons.append(newRibbon)
        ribbonCoord.append((newRibbonX, newRibbonZ))

    # Create street lamps
    leftLampX = -land - lampOffset
    rightLampX = land + lampOffset
    
    for i in range(lampAmount):
        lampZ = (i * lampSpacing) + 10.0
        
        updateLoadingProgress(f"Creating street lamp {(i*2)+1}/{lampAmount*2}")
        rightLamp = streetlamp.streetlamp(rightLampX, lampZ)
        rightLamp.makeDisplayLists()
        alllamps.append(rightLamp)
        
        updateLoadingProgress(f"Creating street lamp {(i*2)+2}/{lampAmount*2}")
        leftLamp = streetlamp.streetlamp(leftLampX, lampZ)
        leftLamp.makeDisplayLists()
        alllamps.append(leftLamp)

    # Create static objects
    updateLoadingProgress("Creating scene")
    staticObjects()
    
    # Initialize lighting
    updateLoadingProgress("Initializing lighting")
    if (applyLighting == True):
        initializeLight()
    
    # Finish loading
    finishLoading()
    
    glutMainLoop()
    
main()