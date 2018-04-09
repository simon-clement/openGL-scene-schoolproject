from src.vertexArray import VertexArray
from src.shader import *
import src
from src.node import Node, SkinningControlNode

# -------------- Deformable Cylinder Mesh  ------------------------------------
class SkinnedCylinder(SkinningControlNode):
    """ Deformable cylinder """
    def __init__(self, sections=11, quarters=20, **params):

        # this "arm" node and its transform serves as control node for bone 0
        # we give it the default identity keyframe transform, doesn't move
        super().__init__({0: (0, 0, 0)}, {0: quaternion()}, {0: 1}, **params)

        # we add a son "forearm" node with animated rotation for the second
        # part of the cylinder
        self.add(SkinningControlNode(
            {0: (0, 0, 0)},
            {0: quaternion(), 2: quaternion_from_euler(90), 4: quaternion()},
            {0: 1}))

        # there are two bones in this animation corresponding to above noes
        bone_nodes = [self, self.children[0]]

        # these bones have no particular offset transform
        bone_offsets = [identity(), identity()]

        # vertices, per vertex bone_ids and weights
        vertices, faces, bone_id, bone_weights = [], [], [], []
        for x_c in range(sections+1):
            for angle in range(quarters):
                # compute vertex coordinates sampled on a cylinder
                z_c, y_c = sincos(360 * angle / quarters)
                vertices.append((x_c - sections/2, y_c, z_c))

                # the index of the 4 prominent bones influencing this vertex.
                # since in this example there are only 2 bones, every vertex
                # is influenced by the two only bones 0 and 1
                bone_id.append((0, 1, 0, 0))

                # per-vertex weights for the 4 most influential bones given in
                # a vec4 vertex attribute. Not using indices 2 & 3 => 0 weight
                # vertex weight is currently a hard transition in the middle
                # of the cylinder
                weight = 0.7 if x_c <= sections/2 else 0.2
                bone_weights.append((weight, 1 - weight, 0, 0))

        # face indices
        faces = []
        for x_c in range(sections):
            for angle in range(quarters):

                # indices of the 4 vertices of the current quad, % helps
                # wrapping to finish the circle sections
                ir0c0 = x_c * quarters + angle
                ir1c0 = (x_c + 1) * quarters + angle
                ir0c1 = x_c * quarters + (angle + 1) % quarters
                ir1c1 = (x_c + 1) * quarters + (angle + 1) % quarters

                # add the 2 corresponding triangles per quad on the cylinder
                faces.extend([(ir0c0, ir0c1, ir1c1), (ir0c0, ir1c1, ir1c0)])

        # the skinned mesh itself. it doesn't matter where in the hierarchy
        # this is added as long as it has the proper bone_node table
        self.add(SkinnedMesh([vertices, bone_weights, bone_id, bone_weights],
                             bone_nodes, bone_offsets, faces))




class SkinnedMesh:
    """class of skinned mesh nodes in scene graph """
    def __init__(self, attributes, bone_nodes, bone_offsets, index=None):

        # setup shader attributes for linear blend skinning shader
        self.vertex_array = VertexArray(attributes, index)

        # feel free to move this up in Viewer as shown in previous practicals
        self.skinning_shader = Shader(SKINNING_VERT, COLOR_FRAG)

        # store skinning data
        self.bone_nodes = bone_nodes
        self.bone_offsets = bone_offsets

    def draw(self, projection, view, _model, **_kwargs):
        """ skinning object draw method """

        shid = self.skinning_shader.glid
        GL.glUseProgram(shid)

        # setup camera geometry parameters
        loc = GL.glGetUniformLocation(shid, 'projection')
        GL.glUniformMatrix4fv(loc, 1, True, projection)
        loc = GL.glGetUniformLocation(shid, 'view')
        GL.glUniformMatrix4fv(loc, 1, True, view)

        # bone world transform matrices need to be passed for skinning
        for bone_id, node in enumerate(self.bone_nodes):
            bone_matrix = node.world_transform @ self.bone_offsets[bone_id]

            bone_loc = GL.glGetUniformLocation(shid, 'boneMatrix[%d]' % bone_id)
            GL.glUniformMatrix4fv(bone_loc, 1, True, bone_matrix)

        # draw mesh vertex array
        self.vertex_array.draw(GL.GL_TRIANGLES)

        # leave with clean OpenGL state, to make it easier to detect problems
        GL.glUseProgram(0)


class Cylinder(Node):
    def __init__(self):
        super().__init__()
        self.add(*src.loaders.load('cylinder.obj'))

class PhongMesh:
    """ Mesh Object, loaded from obj file"""

    def __init__(self, attributes, index):
        self.vertexArray = VertexArray(attributes, index)

    def draw(self, projection, view, model, shader=None,
             color=(1, 1, 1, 1), view_vector=(0, 0, 1), **param):
        if shader is not None:
            GL.glUseProgram(shader.glid)
        viewMatrix_location = \
            GL.glGetUniformLocation(shader.glid, 'viewMatrix')
        projMatrix_location = \
            GL.glGetUniformLocation(shader.glid, 'projMatrix')
        modelMatrix_location = \
            GL.glGetUniformLocation(shader.glid, 'modelMatrix')
        viewVec_location = \
            GL.glGetUniformLocation(shader.glid, 'view')

        GL.glUniformMatrix4fv(modelMatrix_location, 1, True,
                              model)
        GL.glUniformMatrix4fv(viewMatrix_location, 1, True, view)
        GL.glUniformMatrix4fv(projMatrix_location, 1, True, projection)
        GL.glUniform3fv(viewVec_location, 1, view_vector)

        # draw triangle as GL_TRIANGLE vertex array, draw array call
        self.vertexArray.draw(GL.GL_TRIANGLES)


class ColorMesh:
    """ Mesh Object, loaded from obj file"""

    def __init__(self, attributes, index):
        self.vertexArray = VertexArray(attributes, index)

    def draw(self, projection, view, model, shader=None, color=(1,1,1,1), **param):
        if color_shader is not None:
            GL.glUseProgram(shader.glid)
        matrix_location = GL.glGetUniformLocation(shader.glid, 'matrix')

        GL.glUniformMatrix4fv(matrix_location, 1, True,
                              projection * view * model)

        # draw triangle as GL_TRIANGLE vertex array, draw array call
        self.vertexArray.draw(GL.GL_TRIANGLES)


class Pyramid:
    """Pramid object"""

    def __init__(self):

        # triangle position buffer
        position = np.array(((0, 1, 0), (-0.5, 0, 0.5), (.5, 0, .5),
                             (0, 1, 0), (0.5, 0, 0.5), (.5, 0, -.5),
                             (0, 1, 0), (0.5, 0, -0.5), (-.5, 0, -.5),
                             (0, 1, 0), (-0.5, 0, -0.5), (-.5, 0, .5)), 'f')

        couleur = np.array(((0, 1, 0), (1, 0, 1), (.5, 0, .5),
                            (0, 0, 1), (0, 0, 1), (1, 0, 1),
                            (0, 1, 0), (0.5, 0, 0), (.5, 0, 1),
                            (1, 0, 0), (0, 0, 1), (1, 0, .5)), 'f')

        self.vertexArray = VertexArray([position, couleur], None)

    def draw(self, projection, view, model, shader):
        GL.glUseProgram(shader.glid)
        matrix_location = GL.glGetUniformLocation(shader.glid, 'matrix')

        GL.glUniformMatrix4fv(matrix_location, 1, True,
                              projection * view * model)

        # draw triangle as GL_TRIANGLE vertex array, draw array call
        self.vertexArray.draw(GL.GL_TRIANGLES)


# mesh with a texture
class TexturedMesh:

    def __init__(self, texture, attributes, index=None):
        self.vertex_array = VertexArray(attributes, index)
        self.shader = Shader(TEXTURE_VERT, TEXTURE_FRAG)
        self.texture = texture

    def draw(self, projection, view, model, win=None, **_kwargs):

        GL.glUseProgram(self.shader.glid)

        # projection geometry
        loc = GL.glGetUniformLocation(self.shader.glid, 'modelviewprojection')
        GL.glUniformMatrix4fv(loc, 1, True, projection @ view @ model)

        # texture access setups
        loc = GL.glGetUniformLocation(self.shader.glid, 'diffuseMap')
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture.glid)
        GL.glUniform1i(loc, 0)
        self.vertex_array.draw(GL.GL_TRIANGLES)

        # leave clean state for easier debugging
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        GL.glUseProgram(0)

