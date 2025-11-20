from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math, time
import ImportObject


class diamond:
    obj = 0
    displayList = 0
    
    posX = 0.0
    posY = 1.0
    posZ = 0.0

    sizeX = 1.2
    sizeY = 1.2
    sizeZ = 1.2

    rotation = 0.0
    rotationSpeed = 3.0
    bobOffset = 0.0
    bobSpeed = 4.0
    bobHeight = 0.3
    
    useRedVariant = False
    
    def __init__(self, x, z, red=False):
        if red:
            self.obj = ImportObject.ImportedObject("../objects/diamondR")
            self.useRedVariant = True
        else:
            self.obj = ImportObject.ImportedObject("../objects/diamond")
            self.useRedVariant = False
        self.posX = x
        self.posZ = z
        
    def makeDisplayLists(self):
        self.obj.loadOBJ()

        self.displayList = glGenLists(1)
        glNewList(self.displayList, GL_COMPILE)
        self.obj.drawObject()
        glEndList()
    
    def draw(self):
        glPushMatrix()
        
        # Calculate bobbing motion
        bobY = self.posY + math.sin(self.bobOffset) * self.bobHeight
        
        glTranslatef(self.posX, bobY, self.posZ)
        glRotatef(self.rotation, 0.0, 1.0, 0.0)
        glRotatef(self.rotation * 0.5, 1.0, 0.0, 0.0)  # Additional rotation
        glScalef(self.sizeX, self.sizeY, self.sizeZ)

        glCallList(self.displayList)
        glPopMatrix()

    def update(self, deltaTime):
        # Animate rotation and bobbing
        self.rotation += self.rotationSpeed * deltaTime
        self.bobOffset += self.bobSpeed * deltaTime * 0.01
        if self.rotation >= 360.0:
            self.rotation -= 360.0
        
