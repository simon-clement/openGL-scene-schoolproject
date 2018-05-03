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
from src.herbe import creer_herbe
from random import random
from src.texture import Texture
from src.meshes import UIMesh, ConsigneMesh
from src.cylindre import Cylindre, Plan



# -------------- main program and scene setup --------------------------------
def main():
    """ create a window, add scene objects, then run rendering loop """
    viewer = Viewer()

    # Sky box :
    viewer.set_skybox(load_skybox("meshes/sphere.dae", "textures/ciel.png"))

    viewer.add(load_with_hierarchy("meshes/sol.dae")[0])
    viewer.add_element_interacting(Dino(load_skinned("meshes/dinoPlateforme.dae", 0)[0]))

    # ------ AJOUT DE LA FAMILLE DE PTERODACTYLES ---------
    mon_pterosaure = load_skinned("meshes/pterosaur.dae", 1)[0]
    viewer.add(Ptero(mon_pterosaure, 90, 20, 25, 0.7, 8, 0))
    viewer.add(Ptero(mon_pterosaure))
    viewer.add(Ptero(mon_pterosaure, 250, 45, 46, 1, 2, 1))
    viewer.add(Ptero(mon_pterosaure, 300, 50, 30, 1.5, 5))
    viewer.add(Ptero(mon_pterosaure, 30, 60, 40, 0.5, 1, 1))
    viewer.add(Ptero(mon_pterosaure, 190, 70, 50, 1.2, 4))

    # ------- CHARGEMENT DU CUBE (particule) POUR LE GEYSER -------
    viewer.add_element_interacting(load_for_particle("meshes/cube_particle.dae")[0])


    # ---------- CREATION DES ARBRES ---------
    cylindre = Cylindre()
    arb1 = creer_arbre(10, 2, cylindre, (-20, 0, -20))
    viewer.add(arb1)
    """
    arb2 = creer_arbre(10, 3, cylindre, (0, -.5, -25))
    viewer.add(arb2)


    x1 = -30
    x2 = -50
    h = 22
    z1 = -70cylindre
    z2 = -90
    for i in range(4):
        arb = creer_arbre(8 + random() * 4, 2, cylindre,
                          ((x2 - x1) * random() + x1, h, (z2 - z1) * random() + z1))
        viewer.add(arb)

    """

    # la je fais de l'herbe

    plan = Plan()
    erb1 = creer_herbe(plan, 10.0, (0, -.5, -25))
    viewer.add(erb1)

    x1 = -30
    x2 = -50
    h = 22
    z1 = -70
    z2 = -90
    for _ in range(5):
        erb = creer_herbe(plan, 15, ((x2 - x1) * random() + x1, h, (z2 - z1) * random() + z1), 30.0*random())
        viewer.add(erb)



    # ---- CREATION de la jauge de chargement -----
    bleu = [0,0,1]
    rouge = [1, 0, 0]
    vertices = np.array([[0.7, -0.5, 0],
                [0.7, 0.5, 0],
                [0.75, -0.5, 0],
                [0.7, 0.5, 0],
                [0.75, -0.5, 0],
                [0.75,0.5,0]])
    colors = np.array([bleu, rouge, bleu, rouge, bleu, rouge])
    barre_chargement = UIMesh(np.array([vertices, colors]))
    viewer.add_UI(barre_chargement)

    # ---- CREATION DU TEXTE "press space" ---
    vertices2 = np.array([[0.95, -0.85, 0],
                [0.95, -0.65, 0],
                [-0.05, -0.85, 0],
                [0.95, -0.65, 0],
                [-0.05, -0.85, 0],
                [-0.05, -0.65,0]])
    texture = Texture("textures/press.png")
    consigne = ConsigneMesh(texture, [vertices2])
    viewer.add_UI(consigne)

    viewer.run()


if __name__ == '__main__':
    glfw.init()                # initialize window system glfw
    main()                     # main function keeps variables locally scoped
    glfw.terminate()           # destroy all glfw windows and GL contexts
