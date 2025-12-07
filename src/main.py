#!/usr/bin/env python
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math, time, random, csv, datetime
import ImportObject
import PIL.Image as Image
import jeep, cone, star, diamond, ribbon, streetlamp
import shader_utils

windowSize = 600
windowHeight = 600
windowWidth = 1000
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
gameStartTime = 0  # Add game start time tracker

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
prevMouseX = 0.0  # Add previous mouse position tracking
prevMouseY = 0.0
leftMouseDown = False  # Track left mouse button state
rightMouseDown = False  # Track right mouse button state

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

lampLightsEnabled = False  # Toggle for lamp lights
GL_LIGHT_LAMP_START = GL_LIGHT2  # Start from LIGHT2 (LIGHT0 and LIGHT1 may be used)

loadingProgress = 0  # Track loading progress
totalLoadingSteps = 0  # Total number of loading steps
currentLoadingStep = 0  # Current step being processed
showHomeScreen = False  # Add home screen flag
homeScreenTextureID = 0  # Add home screen texture ID

useShaders = False
blinnPhongShader = None
currentShadingModel = "fixed"  # "fixed" or "blinn-phong"


starsCollected = 0

# Add a new global variable to track which ribbons have been used
usedRibbons = set()  # Track indices of ribbons already used

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

def initializeShaders():
    """Initialize shader programs"""
    global blinnPhongShader
    try:
        blinnPhongShader = shader_utils.ShaderProgram(
            '../shaders/blinn_phong.vert',
            '../shaders/blinn_phong.frag'
        )
        print("Blinn-Phong shader loaded successfully")
    except Exception as e:
        print(f"Failed to load shaders: {e}")
        blinnPhongShader = None

def setupShaderUniforms():
    """Setup shader uniforms for current frame"""
    if not blinnPhongShader or not useShaders:
        return
    
    blinnPhongShader.use()
    
    # Get current matrices
    modelview = glGetFloatv(GL_MODELVIEW_MATRIX)
    projection = glGetFloatv(GL_PROJECTION_MATRIX)
    
    # Calculate normal matrix (transpose of inverse of upper-left 3x3 of modelview)
    import numpy as np
    mv_3x3 = modelview[:3, :3]
    normal_matrix = np.linalg.inv(mv_3x3).T
    
    # Set matrices
    blinnPhongShader.set_mat4("modelMatrix", np.eye(4))
    blinnPhongShader.set_mat4("viewMatrix", modelview)
    blinnPhongShader.set_mat4("projectionMatrix", projection)
    blinnPhongShader.set_mat3("normalMatrix", normal_matrix)
    
    # Set material properties
    blinnPhongShader.set_vec3("materialAmbient", matAmbient[0], matAmbient[1], matAmbient[2])
    blinnPhongShader.set_vec3("materialDiffuse", matDiffuse[0], matDiffuse[1], matDiffuse[2])
    blinnPhongShader.set_vec3("materialSpecular", matSpecular[0], matSpecular[1], matSpecular[2])
    blinnPhongShader.set_float("materialShininess", matShininess)
    
    # Set light properties based on current light type
    if currentLightType == "point":
        blinnPhongShader.set_vec3("lightPosition", light0_Position[0], light0_Position[1], light0_Position[2])
    elif currentLightType == "spotlight":
        blinnPhongShader.set_vec3("lightPosition", jeepObj.posX, jeepObj.posY + 10.0, jeepObj.posZ)
    else:
        blinnPhongShader.set_vec3("lightPosition", 0.0, 10.0, 0.0)
    
    blinnPhongShader.set_vec3("lightAmbient", 0.2, 0.2, 0.2)
    blinnPhongShader.set_vec3("lightDiffuse", 0.8, 0.8, 0.8)
    blinnPhongShader.set_vec3("lightSpecular", 1.0, 1.0, 1.0)
    
    # Set view position (camera position)
    blinnPhongShader.set_vec3("viewPosition", eyeX, eyeY, eyeZ)
    
    # Texture settings
    blinnPhongShader.set_int("textureSampler", 0)
    blinnPhongShader.set_bool("useTexture", False)

def display():
    global jeepObj, canStart, score, beginTime, countTime, jeepAccelerated, isLoading, loadingProgress, showHomeScreen, starsCollected
    
    # Show loading screen with progress text only
    if isLoading:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glDisable(GL_LIGHTING)
        
        # Set up orthographic projection for 2D rendering
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        
        # Get current window dimensions
        width = glutGet(GLUT_WINDOW_WIDTH)
        height = glutGet(GLUT_WINDOW_HEIGHT)
        gluOrtho2D(0, width, 0, height)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Draw "Loading..." text (centered)
        glColor3f(1.0, 1.0, 1.0)
        loadingText = f"Loading... {loadingProgress}%"
        textWidth = len(loadingText) * 9  # Approximate pixel width per character
        textX = (width - textWidth) / 2
        textY = height / 2  # Centered vertically
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
        
        # Get current window dimensions
        width = glutGet(GLUT_WINDOW_WIDTH)
        height = glutGet(GLUT_WINDOW_HEIGHT)
        gluOrtho2D(0, width, 0, height)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Draw home screen image as background
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, homeScreenTextureID)
        glColor3f(1.0, 1.0, 1.0)  # White color to show image as-is
        
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex2f(0, 0)
        glTexCoord2f(1.0, 0.0)
        glVertex2f(width, 0)
        glTexCoord2f(1.0, 1.0)
        glVertex2f(width, height)
        glTexCoord2f(0.0, 1.0)
        glVertex2f(0, height)
        glEnd()
        
        glDisable(GL_TEXTURE_2D)
        
        # Disable depth testing for text rendering
        glDisable(GL_DEPTH_TEST)
        
        # Draw "Press SPACE to Start" text (blinking effect)
        blinkTime = int(glutGet(GLUT_ELAPSED_TIME) / 500) % 2  # Blink every 500ms
        if blinkTime == 0:
            glColor3f(1.0, 1.0, 0.0)  # Yellow color
            startText = "Press SPACE to Start"
            
            # Use GLUT_BITMAP_9_BY_15 and draw multiple times for bold effect
            selectedFont = GLUT_BITMAP_9_BY_15
            charWidth = 9
            
            startWidth = len(startText) * charWidth
            startX = (width - startWidth) / 2
            startY = height * 0.2  # Position at 20% from bottom
            
            # Draw text multiple times with slight offsets to simulate bold
            offsets = [(0, 0), (1, 0), (0, 1), (1, 1)]  # Right, down, and diagonal
            
            for offset in offsets:
                glRasterPos2f(startX + offset[0], startY + offset[1])
                for char in startText:
                    glutBitmapCharacter(selectedFont, ord(char))
        
        # Re-enable depth testing
        glEnable(GL_DEPTH_TEST)
        
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

    # Apply lighting or shaders based on mode
    if useShaders and blinnPhongShader:
        glDisable(GL_LIGHTING)
        setupShaderUniforms()
    elif applyLighting == True and currentLightType != "none":
        glEnable(GL_LIGHTING)
        glMaterialfv(GL_FRONT, GL_AMBIENT, matAmbient)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, matDiffuse)
        glMaterialfv(GL_FRONT, GL_SPECULAR, matSpecular)
        glMaterialfv(GL_FRONT, GL_SHININESS, matShininess)
        
        if currentLightType == "spotlight":
            spotlight_pos = [jeepObj.posX, jeepObj.posY + 10.0, jeepObj.posZ, 1.0]
            glLightfv(GL_LIGHT0, GL_POSITION, spotlight_pos)
        
        if currentLightType in ["point", "spotlight"]:
            glDisable(GL_LIGHTING)
            glColor3f(1.0, 1.0, 0.0)
            glPushMatrix()
            
            if currentLightType == "point":
                glTranslatef(light0_Position[0], light0_Position[1], light0_Position[2])
            else:
                glTranslatef(jeepObj.posX, jeepObj.posY + 10.0, jeepObj.posZ)
            
            glutSolidSphere(0.5, 16, 12)
            glPopMatrix()
            glEnable(GL_LIGHTING)
    
    wasLightingEnabled = glIsEnabled(GL_LIGHTING)
    glDisable(GL_LIGHTING)
    
    if useShaders and blinnPhongShader:
        blinnPhongShader.stop()
    
    glColor3f(1.0, 1.0, 1.0)
    shadingInfo = f"Shading: {currentShadingModel.title()}"
    text3d(shadingInfo, -18, 9, 0)
    text3d(f"Lighting: {currentLightType.title()}", -18, 8, 0)

    if useShaders and blinnPhongShader:
        setupShaderUniforms()
    elif wasLightingEnabled:
        glEnable(GL_LIGHTING)
   
    beginTime = 6-score
    countTime = score-6
    if (score <= 5):
        canStart = False
        glDisable(GL_LIGHTING)
        if useShaders and blinnPhongShader:
            blinnPhongShader.stop()
        glColor3f(1.0,0.0,1.0)
        text3d("Begins in: "+str(int(beginTime)), jeepObj.posX, jeepObj.posY + 3.0, jeepObj.posZ)
        if wasLightingEnabled:
            glEnable(GL_LIGHTING)
        if useShaders and blinnPhongShader:
            setupShaderUniforms()
    elif (score <= 6):
        canStart = True
        glDisable(GL_LIGHTING)
        if useShaders and blinnPhongShader:
            blinnPhongShader.stop()
        glColor3f(1.0,0.0,1.0)
        text3d("GO!", jeepObj.posX, jeepObj.posY + 3.0, jeepObj.posZ)
        if wasLightingEnabled:
            glEnable(GL_LIGHTING)
        if useShaders and blinnPhongShader:
            setupShaderUniforms()
    else:
        canStart = True
        glDisable(GL_LIGHTING)
        if useShaders and blinnPhongShader:
            blinnPhongShader.stop()
        glColor3f(0.0,1.0,1.0)
        text3d("Scoring: "+str(int(countTime)), jeepObj.posX, jeepObj.posY + 3.0, jeepObj.posZ)
        if wasLightingEnabled:
            glEnable(GL_LIGHTING)
        if useShaders and blinnPhongShader:
            setupShaderUniforms()

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
    
    if useShaders and blinnPhongShader:
        blinnPhongShader.stop()
    
    # Draw star counter in 2D screen space (upper right corner)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    # Get current window dimensions
    width = glutGet(GLUT_WINDOW_WIDTH)
    height = glutGet(GLUT_WINDOW_HEIGHT)
    gluOrtho2D(0, width, 0, height)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Disable depth test for 2D overlay
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    
    # Draw star counter text
    glColor3f(1.0, 1.0, 0.0)  # Yellow color for stars
    starCountText = f"Stars: {starsCollected}/{starAmount}"
    
    # Calculate text width (approximate)
    textWidth = len(starCountText) * 9  # Approximate pixel width per character
    textX = width - textWidth - 20  # 20 pixels from right edge
    textY = height - 30  # 30 pixels from top
    
    glRasterPos2f(textX, textY)
    for char in starCountText:
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char))
    
    # Restore depth test
    glEnable(GL_DEPTH_TEST)
    
    # Restore matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
    glutSwapBuffers()

def idle():#--------------with more complex display items like turning wheel---
    global tickTime, prevTime, score, jeepAccelerated, accelerationEndTime, gameStartTime
    jeepObj.rotateWheel(-0.1 * tickTime)    
    
    curTime = glutGet(GLUT_ELAPSED_TIME)
    
    # Check if acceleration has expired
    if jeepAccelerated and curTime > accelerationEndTime:
        jeepAccelerated = False
        print("Acceleration ended - returning to normal speed")
    
    # Update automatic objects
    updateAutomaticObjects()
    
    glutPostRedisplay()
    
    tickTime = curTime - prevTime
    prevTime = curTime
    
    # Only update score if game has started (after home screen)
    if gameStartTime > 0:
        score = (curTime - gameStartTime) / 1000
    else:
        score = 0

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
        gluLookAt(jeepObj.posX, cameraHeight, jeepObj.posZ,  # Camera position above jeep (follows jeep)
                  jeepObj.posX, jeepObj.posY, jeepObj.posZ,  # Look at jeep
                  0, 0, 1)         
        print("top view")
    elif (behindView == True):
        # Camera behind the jeep
        cameraDistance = 20.0
        cameraHeight = 10.0
        gluLookAt(jeepObj.posX, jeepObj.posY + cameraHeight, jeepObj.posZ - cameraDistance,  # Camera behind jeep (follows jeep)
                  jeepObj.posX, jeepObj.posY, jeepObj.posZ,  # Look at jeep
                  0, 1, 0)
        print("behind view")
    elif (frontView == True):
        # Camera in front of the jeep
        cameraDistance = 20.0
        cameraHeight = 10.0
        gluLookAt(jeepObj.posX, jeepObj.posY + cameraHeight, jeepObj.posZ + cameraDistance,  # Camera in front of jeep (follows jeep)
                  jeepObj.posX, jeepObj.posY, jeepObj.posZ,  # Look at jeep
                  0, 1, 0)
        print("front view")
    else:
        setObjView()
        return  # Return to avoid double matrix mode setting
    
    glMatrixMode(GL_MODELVIEW)
    glutPostRedisplay()


def setObjView():
    # things to do
    # realize a view following the jeep
    # refer to setview
    global eyeX, eyeY, eyeZ, angle, phi, radius
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
    
    # Use custom camera position if angles have been modified by mouse drag
    if abs(angle) > 0.1 or abs(phi) > 0.1:
        # Camera is being controlled by mouse - use spherical coordinates centered on jeep
        angleRad = math.radians(angle)
        phiRad = math.radians(phi)
        
        # Calculate camera position relative to jeep using spherical coordinates
        eyeX = jeepObj.posX + radius * math.cos(phiRad) * math.sin(angleRad)
        eyeY = jeepObj.posY + radius * math.sin(phiRad) + 2.0
        eyeZ = jeepObj.posZ + radius * math.cos(phiRad) * math.cos(angleRad)
        
        gluLookAt(eyeX, eyeY, eyeZ,  # Camera position (follows jeep)
                  jeepObj.posX, jeepObj.posY, jeepObj.posZ,  # Look at jeep
                  0, 1, 0)  # Up vector
    else:
        # Default camera follows the jeep from behind (back view)
        cameraDistance = 20.0
        cameraHeight = 10.0
        
        # Position camera behind the jeep - FOLLOWING THE JEEP
        cameraX = jeepObj.posX
        cameraY = jeepObj.posY + cameraHeight
        cameraZ = jeepObj.posZ - cameraDistance
        
        # Look at the jeep
        gluLookAt(cameraX, cameraY, cameraZ,  # Camera position (follows jeep)
                jeepObj.posX, jeepObj.posY, jeepObj.posZ,  # Look at jeep
                0, 1, 0)  # Up vector
        
    glMatrixMode(GL_MODELVIEW)
    #glutPostRedisplay()

#-------------------------------------------user inputs------------------
def mouseHandle(button, state, x, y):
    global midDown, nowX, nowY, leftMouseDown, rightMouseDown, prevMouseX, prevMouseY
    
    # Left mouse button - for rotating view
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            leftMouseDown = True
            prevMouseX = x
            prevMouseY = y
        else:
            leftMouseDown = False
    
    # Middle mouse button - existing functionality
    elif button == GLUT_MIDDLE_BUTTON:
        if state == GLUT_DOWN:
            midDown = True
            nowX = x
            nowY = y
        else:
            midDown = False
    
    # Right mouse button is used for menu
    elif button == GLUT_RIGHT_BUTTON:
        if state == GLUT_DOWN:
            rightMouseDown = True
        else:
            rightMouseDown = False


def motionHandle(x,y):
    global angle, phi, nowX, nowY, midDown, eyeX, eyeY, eyeZ, leftMouseDown, prevMouseX, prevMouseY, radius, topView, frontView, behindView
    
    # Left mouse drag - rotate view around the jeep
    if leftMouseDown and not manipulationMode:
        # Disable special views when using mouse rotation
        topView = False
        frontView = False
        behindView = False
        
        # Calculate mouse movement delta
        deltaX = x - prevMouseX
        deltaY = y - prevMouseY
        
        # Update angles based on mouse movement
        # Horizontal movement rotates around Y axis (angle)
        angle += deltaX * 0.3  # Sensitivity factor
        
        # Vertical movement changes elevation (phi)
        phi += deltaY * 0.3
        
        # Clamp phi to prevent flipping upside down
        if phi > 89.0:
            phi = 89.0
        elif phi < -89.0:
            phi = -89.0
        
        # Update previous mouse position
        prevMouseX = x
        prevMouseY = y
        
        # Force view update
        setObjView()
        glutPostRedisplay()
    
    # Middle mouse drag - pan view (existing functionality)
    elif midDown and not manipulationMode:
        diffX = x - nowX
        diffY = y - nowY
        
        eyeX += diffX * 0.02
        eyeZ += diffY * 0.02
        
        nowX = x
        nowY = y
        
        glutPostRedisplay()
    
    # Left mouse drag in manipulation mode - move selected object
    elif leftMouseDown and manipulationMode and selectedObject:
        deltaX = x - prevMouseX
        deltaY = y - prevMouseY
        
        # Move object in X-Z plane
        selectedObject.posX += deltaX * 0.05
        selectedObject.posZ += deltaY * 0.05
        
        prevMouseX = x
        prevMouseY = y
        
        glutPostRedisplay()


def mouseWheelHandle(wheel, direction, x, y):
    global radius, eyeX, eyeY, eyeZ, zoomLevel
    
    if not manipulationMode:
        # Zoom in/out by changing radius
        if direction > 0:
            radius -= 1.0  # Zoom in
            if radius < 2.0:  # Minimum distance
                radius = 2.0
        else:
            radius += 1.0  # Zoom out
            if radius > 50.0:  # Maximum distance
                radius = 50.0
        
        # Force view update
        setObjView()
        glutPostRedisplay()


    
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
    global eyeX, eyeY, eyeZ, angle, radius, helpWindow, centered, helpWin, overReason, topView, behindView, frontView, isFullscreen, jeepAccelerated, showHomeScreen, gameStartTime, manipulationMode, selectedObject, phi
    
    # Handle space key to start game from home screen
    if key == b' ' and showHomeScreen:
        showHomeScreen = False
        gameStartTime = glutGet(GLUT_ELAPSED_TIME)  # Record the time when game starts
        
        # Reset camera angles and position to default behind view
        angle = 0.0
        phi = 0.0
        radius = 10.0
        eyeX = 0.0
        eyeY = 2.0
        eyeZ = 10.0
        topView = False
        frontView = False
        behindView = False
        
        print("Starting game with default camera view!")
        glutPostRedisplay()
        return
    
    # Toggle manipulation mode with 'M' key
    if key == b'm' or key == b'M':
        manipulationMode = not manipulationMode
        if manipulationMode:
            # Set the first star as the selected object (you can change this)
            if len(allstars) > 0:
                selectedObject = allstars[0]
                print("Manipulation mode ON - Use left mouse to drag star")
            else:
                manipulationMode = False
                print("No objects to manipulate")
        else:
            selectedObject = None
            print("Manipulation mode OFF - Use left mouse to rotate view")
        glutPostRedisplay()
        return
    
    # Reset view with 'R' key
    if key == b'r' or key == b'R':
        angle = 0.0
        phi = 0.0
        radius = 10.0
        eyeX = 0.0
        eyeY = 2.0
        eyeZ = 10.0
        topView = False
        frontView = False
        behindView = False
        print("View reset to default following camera")
        setObjView()  # Force view update
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

    global overReason, score, usedDiamond, countTime, jeepAccelerated, accelerationEndTime, starsCollected, usedRibbons
    
    # Check obstacle collisions
    for obstacle in obstacleCoord:
        if dist((jeepObj.posX, jeepObj.posZ), obstacle) <= ckSense:
            overReason = "You hit an obstacle!"
            gameOver()
    
    if (jeepObj.posX >= land or jeepObj.posX <= -land):
        overReason = "You ran off the road!"
        gameOver()

    # Check for ribbon collision (acceleration boost) - ribbons stay visible
    for i, ribbonPos in enumerate(ribbonCoord):
        if i not in usedRibbons and dist((jeepObj.posX, jeepObj.posZ), ribbonPos) <= ckSense:
            print("Acceleration ribbon activated!")
            jeepAccelerated = True
            curTime = glutGet(GLUT_ELAPSED_TIME)
            accelerationEndTime = curTime + accelerationDuration
            usedRibbons.add(i)  # Mark ribbon as used but don't remove it

    # Check star collisions
    starsToRemove = []
    for i, starPos in enumerate(rewardCoord):
        if dist((jeepObj.posX, jeepObj.posZ), starPos) <= ckSense:
            print(f"Star collected! Total: {starsCollected + 1}")
            starsCollected += 1
            starsToRemove.append(i)
    
    # Remove collected stars (in reverse order to maintain indices)
    for i in reversed(starsToRemove):
        rewardCoord.pop(i)
        allstars.pop(i)

    # Check diamond collision
    if (dist((jeepObj.posX, jeepObj.posZ), (diamondObj.posX, diamondObj.posZ)) <= ckSense and usedDiamond ==False):
        print ("Diamond bonus!")
        countTime /= 2
        usedDiamond = True
    
    # Check finish line
    if (jeepObj.posZ >= land*gameEnlarge):
        gameSuccess()

# Update gameOver() to NOT reset stars before showing window
def gameOver():
    global finalScore, usedRibbons, angle, phi
    print ("Game completed!")
    finalScore = score-6
    print(f"Stars collected: {starsCollected}/{starAmount}")
    # Reset camera angles for next game
    angle = 0.0
    phi = 0.0
    usedRibbons.clear()  # Reset used ribbons
    glutHideWindow()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    glutInitWindowSize(200,200)
    glutInitWindowPosition(600,100)
    overWin = glutCreateWindow("Game Over!")
    glutDisplayFunc(overScreen)
    glutMainLoop()
    
# Update gameSuccess() to NOT reset stars before showing window
def gameSuccess():
    global finalScore, usedRibbons, angle, phi
    print ("Game success!")
    finalScore = score-6
    print(f"Stars collected: {starsCollected}/{starAmount}")
    # Reset camera angles for next game
    angle = 0.0
    phi = 0.0
    usedRibbons.clear()  # Reset used ribbons
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
    drawTextBitmap("Your score is: ", -1.0, 0.2)
    glColor3f(1.0,1.0,1.0)
    drawTextBitmap(str(finalScore), -1.0, 0.05)
    
    # Add star count - NOW IT WILL SHOW THE CORRECT VALUE
    glColor3f(1.0, 1.0, 0.0)  # Yellow color for stars
    drawTextBitmap(f"Stars collected: {starsCollected}/{starAmount}", -1.0, -0.2)
    
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
    
    # Add star count to game over screen too
    glColor3f(1.0, 1.0, 0.0)  # Yellow color for stars
    drawTextBitmap(f"Stars collected: {starsCollected}/{starAmount}", -1.0, -0.35)
    
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
    drawTextBitmap("6. Press F to toggle fullscreen" , -1.0, -0.05)
    drawTextBitmap("7. Right-click to change lighting options" , -1.0, -0.2)
    drawTextBitmap("8. Clicking left mouse to drag the view" , -1.0, -0.35)
    glutSwapBuffers()


#----------------------------------------------texture development-----------
def loadTexture(imageName):
    texturedImage = Image.open(imageName)
    
    # Convert image to RGBA mode to ensure consistent handling
    if texturedImage.mode != 'RGBA':
        texturedImage = texturedImage.convert('RGBA')
    
    imgX = texturedImage.size[0]
    imgY = texturedImage.size[1]
    img = texturedImage.tobytes("raw", "RGBA", 0, -1)

    tempID = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tempID)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_MIRRORED_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_MIRRORED_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, imgX, imgY, 0, GL_RGBA, GL_UNSIGNED_BYTE, img)
    return tempID

def loadSceneTextures():
    global roadTextureID, grassTextureID, homeScreenTextureID
    roadTextureID = loadTexture('../img/road2.png')
    grassTextureID = loadTexture('../img/grass.png')
    homeScreenTextureID = loadTexture('../img/home_screen.png')

#-----------------------------------------------lighting work--------------
def initializeLight():
    glEnable(GL_LIGHTING)                
    glEnable(GL_LIGHT0)                 
    glEnable(GL_DEPTH_TEST)              
    glEnable(GL_NORMALIZE)               
    glClearColor(0.1, 0.1, 0.1, 0.0)

def setupLampLights():
    """Set up point lights for each street lamp (2 bulbs per lamp)"""
    global lampLightsEnabled
    
    if not lampLightsEnabled:
        return
    
    # OpenGL typically supports 8 lights, we use LIGHT0 and LIGHT1 for main scene
    # So we can use LIGHT2-LIGHT7 for lamps (6 lights = 3 lamps with 2 bulbs each)
    maxLampLights = min(3, len(alllamps))  # Maximum 3 lamps (6 lights)
    
    for i in range(maxLampLights):
        lamp = alllamps[i]
        
        # First bulb (left)
        lightID1 = GL_LIGHT2 + (i * 2)
        if lightID1 <= GL_LIGHT7:  # Make sure we don't exceed GL_LIGHT7
            glEnable(lightID1)
            
            # Position at the left bulb location
            position1 = [lamp.posX - lamp.bulbOffsetX, lamp.bulbHeight1, lamp.posZ, 1.0]
            
            # Warm ambient lighting
            ambient = [0.2, 0.2, 0.15, 1.0]
            diffuse = [0.6, 0.6, 0.5, 1.0]
            specular = [0.3, 0.3, 0.25, 1.0]
            
            glLightfv(lightID1, GL_POSITION, position1)
            glLightfv(lightID1, GL_AMBIENT, ambient)
            glLightfv(lightID1, GL_DIFFUSE, diffuse)
            glLightfv(lightID1, GL_SPECULAR, specular)
            
            # Set attenuation for realistic falloff
            glLightf(lightID1, GL_CONSTANT_ATTENUATION, 1.0)
            glLightf(lightID1, GL_LINEAR_ATTENUATION, 0.2)
            glLightf(lightID1, GL_QUADRATIC_ATTENUATION, 0.05)
        
        # Second bulb (right)
        lightID2 = GL_LIGHT2 + (i * 2) + 1
        if lightID2 <= GL_LIGHT7:  # Make sure we don't exceed GL_LIGHT7
            glEnable(lightID2)
            
            # Position at the right bulb location
            position2 = [lamp.posX + lamp.bulbOffsetX, lamp.bulbHeight2, lamp.posZ, 1.0]
            
            glLightfv(lightID2, GL_POSITION, position2)
            glLightfv(lightID2, GL_AMBIENT, ambient)
            glLightfv(lightID2, GL_DIFFUSE, diffuse)
            glLightfv(lightID2, GL_SPECULAR, specular)
            
            # Set attenuation for realistic falloff
            glLightf(lightID2, GL_CONSTANT_ATTENUATION, 1.0)
            glLightf(lightID2, GL_LINEAR_ATTENUATION, 0.2)
            glLightf(lightID2, GL_QUADRATIC_ATTENUATION, 0.05)

def disableLampLights():
    """Disable all lamp lights"""
    for i in range(6):
        glDisable(GL_LIGHT2 + i)

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
    
    # Disable lamp lights too
    disableLampLights()
    
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
    global applyLighting, currentLightType, lampLightsEnabled, useShaders, currentShadingModel
    
    if option == 1:
        applyLighting = True
        currentLightType = "ambient"
        useShaders = False
        currentShadingModel = "fixed"
        setupAmbientLight()
        print("ambient")
    elif option == 2:
        applyLighting = True
        currentLightType = "point"
        useShaders = False
        currentShadingModel = "fixed"
        setupPointLight()
        print("point")
    elif option == 3:
        applyLighting = True
        currentLightType = "directional"
        useShaders = False
        currentShadingModel = "fixed"
        setupDirectionalLight()
        print("directional")
    elif option == 4:
        applyLighting = True
        currentLightType = "spotlight"
        useShaders = False
        currentShadingModel = "fixed"
        setupSpotlight()
        print("spotlight")
    elif option == 5:
        applyLighting = False
        currentLightType = "none"
        useShaders = False
        currentShadingModel = "fixed"
        resetLightingState()
        lampLightsEnabled = False
        print("Reset")
    elif option == 6:
        lampLightsEnabled = not lampLightsEnabled
        if lampLightsEnabled:
            setupLampLights()
            print("Street lamp lights enabled")
        else:
            disableLampLights()
            print("Street lamp lights disabled")
    elif option == 7:
        # Toggle Blinn-Phong shader
        useShaders = not useShaders
        if useShaders:
            applyLighting = False
            currentShadingModel = "blinn-phong"
            glDisable(GL_LIGHTING)
            print("Blinn-Phong shader enabled")
        else:
            currentShadingModel = "fixed"
            print("Blinn-Phong shader disabled")

    print(f"Current Light Type: {currentLightType}, Shading Model: {currentShadingModel}")
    glutPostRedisplay()
    return 0  # Add explicit return value for GLUT callback

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
    glutInitWindowSize(windowWidth, windowHeight)
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
    
    # Calculate total loading steps BEFORE any updateLoadingProgress calls
    totalLoadingSteps = (
        1 +  # Initialize shaders
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
    glutSwapBuffers()
    glutMainLoopEvent()
    
    # Add small delay to ensure window is fully initialized
    import time
    time.sleep(0.1)
    
    # Initialize shaders
    updateLoadingProgress("Initializing shaders")
    initializeShaders()
    
    # Update menu
    glutCreateMenu(myMenu)
    glutAddMenuEntry("Ambient Light", 1)
    glutAddMenuEntry("Point Light", 2)
    glutAddMenuEntry("Directional Light", 3)
    glutAddMenuEntry("Spotlight", 4)
    glutAddMenuEntry("No Lighting", 5)
    glutAddMenuEntry("Toggle Lamp Lights", 6)
    glutAddMenuEntry("Toggle Blinn-Phong Shader", 7)
    glutAttachMenu(GLUT_RIGHT_BUTTON)

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