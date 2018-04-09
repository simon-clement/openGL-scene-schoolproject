import OpenGL.GL as GL              # standard Python OpenGL wrapper
import os                           # os function, i.e. checking file status

# ------------ low level OpenGL object wrappers ----------------------------
class Shader:
    """ Helper class to create and automatically destroy shader program """
    @staticmethod
    def _compile_shader(src, shader_type):
        src = open(src, 'r').read() if os.path.exists(src) else src
        src = src.decode('ascii') if isinstance(src, bytes) else src
        shader = GL.glCreateShader(shader_type)
        GL.glShaderSource(shader, src)
        GL.glCompileShader(shader)
        status = GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS)
        src = ('%3d: %s' % (i+1, l) for i, l in enumerate(src.splitlines()))
        if not status:
            log = GL.glGetShaderInfoLog(shader).decode('ascii')
            GL.glDeleteShader(shader)
            src = '\n'.join(src)
            print('Compile failed for %s\n%s\n%s' % (shader_type, log, src))
            return None
        return shader

    def __init__(self, vertex_source, fragment_source):
        """ Shader can be initialized with raw strings or source file names """
        self.glid = None
        vert = self._compile_shader(vertex_source, GL.GL_VERTEX_SHADER)
        frag = self._compile_shader(fragment_source, GL.GL_FRAGMENT_SHADER)
        if vert and frag:
            self.glid = GL.glCreateProgram()  # pylint: disable=E1111
            GL.glAttachShader(self.glid, vert)
            GL.glAttachShader(self.glid, frag)
            GL.glLinkProgram(self.glid)
            GL.glDeleteShader(vert)
            GL.glDeleteShader(frag)
            status = GL.glGetProgramiv(self.glid, GL.GL_LINK_STATUS)
            if not status:
                print(GL.glGetProgramInfoLog(self.glid).decode('ascii'))
                GL.glDeleteProgram(self.glid)
                self.glid = None

    def __del__(self):
        GL.glUseProgram(0)
        if self.glid:                      # if this is a valid shader object
            GL.glDeleteProgram(self.glid)  # object dies => destroy GL object


# ------------  Simple illumination shaders ----------------------
LAMBERTIAN_VERT = """#version 330 core
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normal;
uniform mat4 viewMatrix;
uniform mat4 modelMatrix;
uniform mat4 projMatrix;
out vec3 outNormal;
void main() {
    gl_Position = projMatrix * (viewMatrix * (modelMatrix * vec4(position, 1)));
    mat4 modV = viewMatrix * modelMatrix;
    mat3 M = mat3(vec3(modV[0]), vec3(modV[1]), vec3(modV[2]));
    outNormal = transpose(inverse(M)) * normal;
}"""

LAMBERTIAN_FRAG = """#version 330 core
in vec3 outNormal;
out vec4 color;
uniform vec3 view;
void main() {
    vec4 ambiant = vec4(0.1,0,0,1);
    vec4 ambiantReflect = vec4(0,1,0,1);
    vec3 normal = normalize(outNormal);
    vec3 l = vec3(0, -1, 0);
    vec4 col = vec4(0.5, 0.5, 0.5, 1);
    float dotP = max(0, dot(normal, l));
    float s = 15;
    float dotS = max(0, pow(dot(reflect(l, normal), view), s));
    color = col*dotP + ambiant + ambiantReflect * dotS;
}"""


# ------------  Simple color shaders ------------------------------------------
COLOR_VERT = """#version 330 core
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 color;

uniform mat4 modelviewprojection;
out vec3 fragColor;

void main() {
    gl_Position = modelviewprojection * vec4(position, 1);
    fragColor = color;
}"""


COLOR_FRAG = """#version 330 core
in vec3 fragColor;
out vec4 outColor;
void main() {
    outColor = vec4(fragColor, 1);
}"""


# -------------- Linear Blend Skinning : TP7 ---------------------------------
MAX_VERTEX_BONES = 4
MAX_BONES = 128

# new shader for skinned meshes, fully compatible with previous color fragment
SKINNING_VERT = """#version 330 core
// ---- camera geometry
uniform mat4 projection, view;

// ---- skinning globals and attributes
const int MAX_VERTEX_BONES=%d, MAX_BONES=%d;
uniform mat4 boneMatrix[MAX_BONES];

// ---- vertex attributes
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 color;
layout(location = 2) in vec4 bone_ids;
layout(location = 3) in vec4 bone_weights;

// ----- interpolated attribute variables to be passed to fragment shader
out vec3 fragColor;

void main() {
    vec4 weight = normalize(bone_weights);
    // ------ creation of the skinning deformation matrix
    mat4 matrice1 = weight.x*boneMatrix[int(bone_ids[0])];
    mat4 matrice2 = weight.y*boneMatrix[int(bone_ids[1])];
    mat4 matrice3 = weight.z*boneMatrix[int(bone_ids[2])];
    mat4 matrice4 = weight.w*boneMatrix[int(bone_ids[3])];
    mat4 skinMatrix = matrice1 + matrice2 + matrice3 + matrice4;

    // ------ compute world and normalized eye coordinates of our vertex
    vec4 wPosition4 = skinMatrix * vec4(position, 1.0);
    gl_Position = projection * view * wPosition4;
    
    fragColor = color;
}
""" % (MAX_VERTEX_BONES, MAX_BONES)



# -------------- texture shaders----------------------------------
TEXTURE_VERT = """#version 330 core
uniform mat4 modelviewprojection;
layout(location = 0) in vec3 position;
layout(location = 1) in vec2 uvCoords;
out vec2 fragTexCoord;
void main() {
    gl_Position = modelviewprojection * vec4(position, 1);
    fragTexCoord = uvCoords;
}"""

TEXTURE_FRAG = """#version 330 core
uniform sampler2D diffuseMap;
in vec2 fragTexCoord;
out vec4 outColor;
void main() {
    outColor = texture(diffuseMap, fragTexCoord);
}"""

