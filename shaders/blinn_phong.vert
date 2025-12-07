#version 120

// Vertex attributes
attribute vec3 position;
attribute vec3 normal;
attribute vec2 texCoord;

// Uniforms
uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform mat3 normalMatrix;

// Outputs to fragment shader
varying vec3 fragPosition;
varying vec3 fragNormal;
varying vec2 fragTexCoord;

void main()
{
    // Transform vertex position
    vec4 worldPos = modelMatrix * vec4(position, 1.0);
    fragPosition = worldPos.xyz;
    
    // Transform normal
    fragNormal = normalize(normalMatrix * normal);
    
    // Pass texture coordinates
    fragTexCoord = texCoord;
    
    // Final position
    gl_Position = projectionMatrix * viewMatrix * worldPos;
}