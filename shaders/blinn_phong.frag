#version 120

// Inputs from vertex shader
varying vec3 fragPosition;
varying vec3 fragNormal;
varying vec2 fragTexCoord;

// Material properties
uniform vec3 materialAmbient;
uniform vec3 materialDiffuse;
uniform vec3 materialSpecular;
uniform float materialShininess;

// Light properties
uniform vec3 lightPosition;
uniform vec3 lightAmbient;
uniform vec3 lightDiffuse;
uniform vec3 lightSpecular;
uniform vec3 viewPosition;

// Texture
uniform sampler2D textureSampler;
uniform bool useTexture;

void main()
{
    // Normalize interpolated normal
    vec3 normal = normalize(fragNormal);
    
    // Calculate light direction
    vec3 lightDir = normalize(lightPosition - fragPosition);
    
    // Calculate view direction
    vec3 viewDir = normalize(viewPosition - fragPosition);
    
    // Calculate halfway vector (Blinn-Phong)
    vec3 halfwayDir = normalize(lightDir + viewDir);
    
    // Ambient component
    vec3 ambient = lightAmbient * materialAmbient;
    
    // Diffuse component
    float diff = max(dot(normal, lightDir), 0.0);
    vec3 diffuse = lightDiffuse * (diff * materialDiffuse);
    
    // Specular component (Blinn-Phong)
    float spec = pow(max(dot(normal, halfwayDir), 0.0), materialShininess);
    vec3 specular = lightSpecular * (spec * materialSpecular);
    
    // Combine lighting
    vec3 result = ambient + diffuse + specular;
    
    // Apply texture if enabled
    if (useTexture) {
        vec4 texColor = texture2D(textureSampler, fragTexCoord);
        result *= texColor.rgb;
    }
    
    gl_FragColor = vec4(result, 1.0);
}