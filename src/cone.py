from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math, time, random
import ImportObject


class cone:
    obj = 0
    displayList = 0
    
    posX = 0.0
    posY = 0.0
    posZ = 0.0

    sizeX = 1.0
    sizeY = 1.0
    sizeZ = 1.0

    rotation = 0.0
    
    def __init__(self, x, z):
        self.obj = ImportObject.ImportedObject("../objects/cone")
        self.posX = x
        self.posZ = z

        # Add movement properties
        self.moveSpeed = 0.1
        self.direction = random.choice([-1, 1])  # Random initial direction
        self.moveRange = 5.0  # How far it can move from start
        self.originalX = x
        self.isAutomatic = False  # Flag to identify automatic cones
        
    def update(self, land, jeepObj, allCones):
        """Update automatic cone movement and reactions"""
        if not self.isAutomatic:
            return
            
        # Move the cone
        self.posX += self.direction * self.moveSpeed
        
        # Boundary checking - reverse direction if hitting boundaries
        if self.posX >= land or self.posX <= -land:
            self.direction *= -1
            
        # Stay within movement range of original position
        if abs(self.posX - self.originalX) > self.moveRange:
            self.direction *= -1
            
        # React to jeep proximity - speed up when jeep is near
        distanceToJeep = math.sqrt((self.posX - jeepObj.posX)**2 + (self.posZ - jeepObj.posZ)**2)
        if distanceToJeep < 15.0:
            self.moveSpeed = 0.2  # Speed up
        else:
            self.moveSpeed = 0.1  # Normal speed
            
        # Avoid collision with other cones
        for otherCone in allCones:
            if otherCone != self:
                distance = math.sqrt((self.posX - otherCone.posX)**2 + (self.posZ - otherCone.posZ)**2)
                if distance < 3.0:  # Too close to another cone
                    self.direction *= -1
                    break
        
    def makeDisplayLists(self):
        self.obj.loadOBJ()

        self.displayList = glGenLists(1)
        glNewList(self.displayList, GL_COMPILE)
        self.obj.drawObject()
        glEndList()
    
    def draw(self):
        glPushMatrix()
        
        glTranslatef(self.posX,self.posY,self.posZ)
        #glRotatef(self.rotation,0.0,1.0,0.0)
        glScalef(self.sizeX,self.sizeY,self.sizeZ)

        glCallList(self.displayList)
        glPopMatrix()

            
        
