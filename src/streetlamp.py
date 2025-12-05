from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import ImportObject

class streetlamp:
    def __init__(self, x, z):
        self.posX = x
        self.posY = 0.0
        self.posZ = z
        self.scale = 0.05  # Much smaller scale
        self.rotation = 0.0
        self.obj = ImportObject.ImportedObject('../objects/Street_Lamp')
        
    def makeDisplayLists(self):
        """Create display list for the street lamp"""
        self.obj.loadOBJ()
        self.displayList = glGenLists(1)
        glNewList(self.displayList, GL_COMPILE)
        self.drawLamp()
        glEndList()
    
    def drawLamp(self):
        """Draw the street lamp model with texture"""
        # Enable texturing if the object has textures
        if self.obj.hasTex:
            glEnable(GL_TEXTURE_2D)
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        
        # Draw each face
        for face in self.obj.faces:
            # Check if this is a material definition
            if isinstance(face[0], int) and face[0] == -1:
                # Set material color if available
                if len(face) > 1 and isinstance(face[1], str):
                    self.setMaterialColor(face[1])
                continue
            
            glBegin(GL_POLYGON)
            for f in face:
                # Apply texture coordinates if available
                if len(f) > 1 and f[1] != -1 and f[1] < len(self.obj.texCoords):
                    glTexCoord2f(self.obj.texCoords[f[1]][0],
                                self.obj.texCoords[f[1]][1])
                
                # Apply normals if available
                if len(f) > 2 and f[2] != -1 and f[2] < len(self.obj.norms):
                    glNormal3f(self.obj.norms[f[2]][0],
                              self.obj.norms[f[2]][1],
                              self.obj.norms[f[2]][2])
                
                # Apply vertex
                if f[0] < len(self.obj.verts):
                    glVertex3f(self.obj.verts[f[0]][0],
                              self.obj.verts[f[0]][1],
                              self.obj.verts[f[0]][2])
            glEnd()
        
        if self.obj.hasTex:
            glDisable(GL_TEXTURE_2D)
    
    def setMaterialColor(self, materialName):
        """Set material color from loaded materials"""
        for mat in self.obj.materials:
            if mat[0] == materialName:
                # Set diffuse color if available (check if it's not None first)
                if len(mat) > 3 and mat[3] is not None and len(mat[3]) >= 3:
                    glColor3f(mat[3][0], mat[3][1], mat[3][2])
                    # Set material properties for lighting
                    glMaterialfv(GL_FRONT, GL_DIFFUSE, mat[3] + [1.0])
                else:
                    glColor3f(0.7, 0.7, 0.7)  # Default gray
                
                # Set ambient if available
                if len(mat) > 2 and mat[2] is not None and len(mat[2]) >= 3:
                    glMaterialfv(GL_FRONT, GL_AMBIENT, mat[2] + [1.0])
                
                # Set specular if available
                if len(mat) > 4 and mat[4] is not None and len(mat[4]) >= 3:
                    glMaterialfv(GL_FRONT, GL_SPECULAR, mat[4] + [1.0])
                
                # Set shininess if available (mat[1] should be a float)
                if len(mat) > 1 and mat[1] is not None:
                    if isinstance(mat[1], (int, float)):
                        glMaterialfv(GL_FRONT, GL_SHININESS, [mat[1]])
                
                # Bind texture if available
                if len(mat) > 5 and mat[5] is not None:
                    glBindTexture(GL_TEXTURE_2D, mat[5])
                
                break
    
    def draw(self):
        """Draw the street lamp at its position"""
        glPushMatrix()
        glTranslatef(self.posX, self.posY, self.posZ)
        glScalef(self.scale, self.scale, self.scale)
        glRotatef(self.rotation, 0, 1, 0)
        
        if hasattr(self, 'displayList'):
            glCallList(self.displayList)
        else:
            self.drawLamp()
        
        glPopMatrix()