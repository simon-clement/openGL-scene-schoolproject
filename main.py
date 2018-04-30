#!/usr/bin/env python3
"""
Python OpenGL practical application.
"""
# Python built-in modules
import os                           # os function, i.e. checking file status
from itertools import cycle
import sys
from bisect import bisect_left      # search sorted keyframe lists

# External, non built-in modules
import OpenGL.GL as GL              # standard Python OpenGL wrapper
import glfw                         # lean window system wrapper for OpenGL
import numpy as np                  # all matrix manipulations & OpenGL args
import pyassimp                     # 3D ressource loader
import pyassimp.errors              # assimp error management + exceptions

from src.transform import translate, scale, identity, Trackball, sincos
from src.transform import (lerp, quaternion_slerp, quaternion_matrix, quaternion,
                       quaternion_from_euler)
from src.animation import *
from src.shader import Shader, COLOR_VERT, COLOR_FRAG
from src.vertexArray import VertexArray
from src.node import *
from src.viewer import Viewer
from src.interaction import GLFWTrackball
from src.loaders import load_skinned, load_skybox, load_with_hierarchy, \
    load_for_particle, load_textured
from src.dino import Dino, Ptero



# -------------- main program and scene setup --------------------------------
def main():
    """ create a window, add scene objects, then run rendering loop """
    viewer = Viewer()

    # Sky box :
    viewer.add(load_skybox("sphere.dae", "ciel.png"))

    viewer.add(load_with_hierarchy("sol.dae")[0])
    viewer.add_element_interacting(Dino(load_skinned("dinoPlateforme.dae")[0]))
    viewer.add(Ptero(load_skinned("pterosaur.dae")[0]))
    viewer.add_element_interacting(load_for_particle("cube_particle.dae")[0])



    # if len(sys.argv) < 2:
    #     print('Cylinder skinning demo.')
    #     print('Note:\n\t%s [3dfile]*\n\n3dfile\t\t the filename of a model in'
    #           ' format supported by pyassimp.' % sys.argv[0])
    #     viewer.add(SkinnedCylinder())
    # else:
    #     viewer.add(*[m for file in sys.argv[1:] for m in load_skinned(file)])

    # start rendering loop
    viewer.run()


if __name__ == '__main__':
    glfw.init()                # initialize window system glfw
    main()                     # main function keeps variables locally scoped
    glfw.terminate()           # destroy all glfw windows and GL contexts
