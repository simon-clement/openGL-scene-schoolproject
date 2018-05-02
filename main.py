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
from src.arbre import creer_arbre
from src.cylindre import Cylindre
from random import random



# -------------- main program and scene setup --------------------------------
def main():
    """ create a window, add scene objects, then run rendering loop """
    viewer = Viewer()

    # Sky box :
    # viewer.add(load_skybox("sphere.dae", "ciel2.png"))
# 
    # viewer.add(load_with_hierarchy("sol.dae")[0])
    # viewer.add_element_interacting(Dino(load_skinned("dinoPlateforme.dae")[0]))
    # viewer.add(Ptero(load_skinned("pterosaur.dae")[0]))
    # viewer.add_element_interacting(load_for_particle("cube_particle.dae")[0])
# 
    # viewer.add_element_interacting(Dino(load_skinned("dinoPlateforme.dae")[0]))

    cylindre = Cylindre()
    # arb1 = creer_arbre(10, 3, cylindre, (-20, 0, -20))
    # viewer.add(arb1)
    # arb2 = creer_arbre(10, 4, cylindre, (0, -.5, -25))
    # viewer.add(arb2)
    l = 80
    for i in range(15):
        arb = creer_arbre(8 + random() * 4, int(random() * 2) + 3, cylindre,
                          (l * random() - l / 2, 0, l * random() - l / 2))
        viewer.add(arb)


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
