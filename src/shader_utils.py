from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import os

class ShaderProgram:
    def __init__(self, vertex_path, fragment_path):
        self.program = None
        self.vertex_shader = None
        self.fragment_shader = None
        self.uniforms = {}
        
        self.load_shaders(vertex_path, fragment_path)
    
    def load_shaders(self, vertex_path, fragment_path):
        """Load and compile shaders"""
        try:
            # Read shader source files
            with open(vertex_path, 'r') as f:
                vertex_source = f.read()
            
            with open(fragment_path, 'r') as f:
                fragment_source = f.read()
            
            # Compile shaders
            self.vertex_shader = compileShader(vertex_source, GL_VERTEX_SHADER)
            self.fragment_shader = compileShader(fragment_source, GL_FRAGMENT_SHADER)
            
            # Link program
            self.program = compileProgram(self.vertex_shader, self.fragment_shader)
            
            print(f"Shader program compiled successfully: {vertex_path}, {fragment_path}")
            
        except Exception as e:
            print(f"Error loading shaders: {e}")
            self.program = None
    
    def use(self):
        """Activate this shader program"""
        if self.program:
            glUseProgram(self.program)
    
    def stop(self):
        """Deactivate shader program"""
        glUseProgram(0)
    
    def get_uniform_location(self, name):
        """Get uniform location, cached"""
        if name not in self.uniforms:
            self.uniforms[name] = glGetUniformLocation(self.program, name)
        return self.uniforms[name]
    
    def set_mat4(self, name, matrix):
        """Set 4x4 matrix uniform"""
        loc = self.get_uniform_location(name)
        glUniformMatrix4fv(loc, 1, GL_FALSE, matrix)
    
    def set_mat3(self, name, matrix):
        """Set 3x3 matrix uniform"""
        loc = self.get_uniform_location(name)
        glUniformMatrix3fv(loc, 1, GL_FALSE, matrix)
    
    def set_vec3(self, name, x, y, z):
        """Set vec3 uniform"""
        loc = self.get_uniform_location(name)
        glUniform3f(loc, x, y, z)
    
    def set_float(self, name, value):
        """Set float uniform"""
        loc = self.get_uniform_location(name)
        glUniform1f(loc, value)
    
    def set_int(self, name, value):
        """Set int uniform"""
        loc = self.get_uniform_location(name)
        glUniform1i(loc, value)
    
    def set_bool(self, name, value):
        """Set bool uniform"""
        loc = self.get_uniform_location(name)
        glUniform1i(loc, 1 if value else 0)
    
    def cleanup(self):
        """Delete shader program"""
        if self.program:
            glDeleteProgram(self.program)