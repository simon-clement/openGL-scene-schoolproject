import OpenGL.GL as GL              # standard Python OpenGL wrapper
import os                           # os function, i.e. checking file status

# ------------ low level OpenGL object wrappers ----------------------------
GEYSER_SHADER_ID = 0
LAMBERTIAN_SHADER_ID = 1
COLOR_SHADER_ID = 2
SKYBOX_SHADER_ID = 3
UI_SHADER_ID = 4

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
    gl_Position = projMatrix * viewMatrix * modelMatrix * vec4(position, 1);
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
    vec3 normal = normalize(outNormal);
    vec3 l = vec3(0, 0, 1);
    vec4 col = vec4(1, 0.8, 0.6, 1);
    float dotP = max(0, dot(normal, l));
    color = col*dotP + ambiant;
}"""


# ----------- create shaders for geysers ------------
# id is the id of the particle. We need to specify a position/scale_transparency in the shader
# that depends on time and on id
# (id will be more or less the seed of a continuous random generator)
PARTICLE_PER_TIME = 400
TIME_RISING = 0.401
NUMBER_PARTICLES = 200

GEYSER_PARTICLE_VERT = """#version 330 core
layout(location = 0) in vec3 position;
uniform mat4 viewMatrix;
uniform mat4 projMatrix;
uniform float id_particle;
uniform float time;
uniform float height_geyser;
out vec3 cubePos;

vec3 echelle(float temps_propre) {
    float first_scale = 1.5;
    vec3 base = vec3(sin(id_particle) + 1.1,
                cos(id_particle) + 1.1,
                sin(id_particle+3.14/4) + 1.2);
    return base * pow(first_scale + temps_propre, 1.3);
}

vec3 position_particle(float temps_propre) {
    const vec2 dir_vent = vec2(0.3, 0.2);
    float vitesse_propre_horizontal = 8.5 + 4 * sin(id_particle*28);
    vec2 depl_h = vitesse_propre_horizontal * dir_vent * temps_propre;

    const float time_rising = %(time_rising)f;
    float time_borne = min(temps_propre, time_rising) / time_rising;
    float cste_hauteur_max = height_geyser *
            ((%(number_particles)f - id_particle) / (%(number_particles)f));
            //(%(particle_per_time)f * %(time_rising)f));
    float pos_z = time_borne * abs(sin(91 * id_particle)) * cste_hauteur_max * (0.9 - time_borne*time_borne/3) - 4;
    return vec3(depl_h, pos_z);
}


mat4 rotationMatrix(vec3 axis, float angle)
{
    axis = normalize(axis);
    float s = sin(angle);
    float c = cos(angle);
    float oc = 1.0 - c;

    return mat4(oc * axis.x * axis.x + c, oc * axis.x * axis.y - axis.z * s,  oc * axis.z * axis.x + axis.y * s,  0.0,
            oc * axis.x * axis.y + axis.z * s,  oc * axis.y * axis.y + c, oc * axis.y * axis.z - axis.x * s,  0.0,
            oc * axis.z * axis.x - axis.y * s,  oc * axis.y * axis.z + axis.x * s,  oc * axis.z * axis.z + c, 0.0,
            0.0, 0.0, 0.0, 1.0);
                                                        }
void main() {
    cubePos = position;
    vec4 pos;

    float temps_propre = max(time-id_particle/%(particle_per_time)f,0);

    pos.xyz = position.xyz * echelle(temps_propre);
    pos.w = 1;

    float rand1 = sin(id_particle * 100);
    float rand2 = cos(id_particle * 100);
    float rand3 = sin(id_particle * 200);
    vec3 axis = vec3(rand1, rand2, rand3);
    pos = rotationMatrix(axis, 0.8) * pos;

    pos.xyz = pos.xyz + position_particle(temps_propre);

    gl_Position = projMatrix * viewMatrix * pos;
}
""" % {"particle_per_time" : PARTICLE_PER_TIME,
        "time_rising" : TIME_RISING,
        "number_particles" : NUMBER_PARTICLES}

GEYSER_PARTICLE_FRAG = """#version 330 core
in vec3 cubePos;
out vec4 color;
uniform float id_particle;
uniform float time;

float transparence(vec3 pos, float temps_propre){
    float rayon = 0.5 + sin(id_particle + time) / 5;
    float distance_centre = (length(pos) - 1) / (sqrt(3.) - 1);
    if (distance_centre > rayon) {
        return 0.0;
    } else {
        float fading = max(0, time - %(time_rising)f);
        return exp(-fading - 1 - 1/(1 - distance_centre/rayon));
    }
}

void main() {
    float temps_propre = (time-id_particle/%(particle_per_time)f)/%(time_rising)f;
    if (temps_propre < 0) {
        discard;
    }
    float blank = transparence(cubePos, temps_propre);
    vec4 col = vec4(0.8, 1, 0.8, blank);
    color = col;
}

""" % {"particle_per_time" : PARTICLE_PER_TIME,
        "time_rising" : TIME_RISING}

# ------------  Simple UI shaders ------------------------------------------
UI_VERT = """#version 330 core
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 color;

out vec3 fragColor;
void main() {
    gl_Position = vec4(position, 1);
    fragColor = color;
}"""


UI_FRAG = """#version 330 core
in vec3 fragColor;
uniform float charge;
out vec4 outColor;
void main() {
    if (charge > fragColor.r) {
        outColor = vec4(fragColor, 1);
    } else {
        outColor = vec4(1, 1, 1, 0.4);
    }
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

# -------------- skybox shaders----------------------------------
SKYBOX_VERT = """#version 330 core
uniform mat4 modelviewprojection;
layout(location = 0) in vec3 position;
out vec2 fragTexCoord;
void main() {
    vec3 position2 = position*1000; // taille sphere * 10000
    vec4 position3D = modelviewprojection * vec4(position2, 1);
    gl_Position = position3D;
    float latitude =  - (position[1]/2 - 0.5);
    float longitude = atan(abs(position[2])/abs((position[0])))*2 ;
    fragTexCoord = vec2(longitude, latitude);
}"""

SKYBOX_FRAG = """#version 330 core
uniform sampler2D diffuseMap;
in vec2 fragTexCoord;
out vec4 outColor;
void main() {
    outColor = texture(diffuseMap, fragTexCoord);
}"""
