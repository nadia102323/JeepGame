from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import PIL.Image as Image

class ribbon:
    def __init__(self, x, z):
        self.posX = x
        self.posY = 0.5  # Slightly above ground
        self.posZ = z
        self.width = 15.0  # Half of road width (land = 20)
        self.depth = 9.0   # Depth of the ribbon
        self.textureID = None
        
    def loadTexture(self, imageName):
        """Load texture for the ribbon"""
        try:
            texturedImage = Image.open(imageName)
            imgX = texturedImage.size[0]
            imgY = texturedImage.size[1]
            img = texturedImage.tobytes("raw", "RGBA", 0, -1)
            
            self.textureID = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.textureID)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, imgX, imgY, 0, GL_RGBA, GL_UNSIGNED_BYTE, img)
            print(f"Ribbon texture loaded successfully from {imageName}")
        except Exception as e:
            print(f"Error loading ribbon texture: {e}")

    
    def makeDisplayLists(self):
        """Create display list for the ribbon"""
        self.displayList = glGenLists(1)
        glNewList(self.displayList, GL_COMPILE)
        self.drawRibbon()
        glEndList()
    
    def drawRibbon(self):
        """Draw a textured quad for the ribbon"""
        if self.textureID is None:
            # Draw a simple colored quad if texture not loaded
            glColor4f(0.0, 1.0, 1.0, 0.8)  # Cyan color
            glBegin(GL_QUADS)
            glVertex3f(-self.width/2, 0, -self.depth/2)
            glVertex3f(self.width/2, 0, -self.depth/2)
            glVertex3f(self.width/2, 0, self.depth/2)
            glVertex3f(-self.width/2, 0, self.depth/2)
            glEnd()
        else:
            # Draw textured quad
            glEnable(GL_TEXTURE_2D)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glBindTexture(GL_TEXTURE_2D, self.textureID)
            
            glColor4f(1.0, 1.0, 1.0, 1.0)  # White to show texture colors
            glBegin(GL_QUADS)
            glTexCoord2f(0.0, 0.0)
            glVertex3f(-self.width/2, 0, -self.depth/2)
            glTexCoord2f(1.0, 0.0)
            glVertex3f(self.width/2, 0, -self.depth/2)
            glTexCoord2f(1.0, 1.0)
            glVertex3f(self.width/2, 0, self.depth/2)
            glTexCoord2f(0.0, 1.0)
            glVertex3f(-self.width/2, 0, self.depth/2)
            glEnd()
            
            glDisable(GL_TEXTURE_2D)
            glDisable(GL_BLEND)
    
    
    def draw(self):
        """Draw the ribbon at its position"""
        glPushMatrix()
        glTranslatef(self.posX, self.posY, self.posZ)
        
        if hasattr(self, 'displayList'):
            glCallList(self.displayList)
        else:
            self.drawRibbon()
        
        glPopMatrix()