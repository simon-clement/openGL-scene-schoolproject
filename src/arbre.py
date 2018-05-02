#!/usr/bin/env python3
"""
Python OpenGL dinosaurus : sweet and flying with geysers
"""

import glfw                         # lean window system wrapper for OpenGL
from src.transform import rotate, translate, scale
from src.node import Node
from src.cylindre import Cylindre
from random import random
import numpy as np


def arbre(profondeur, cylindre, angle_x=0, angle_z=0):
    transform = (translate(0, 1, 0)
            @ rotate(axis=(0,1,0), radians=(angle_z))
            @ rotate(axis=(1,0,0), radians=(angle_x))
            @ scale(.7))
    tronc = Node(name='arbre', transform=transform)
    tronc.add(cylindre)
    nb_branches = int(random() * 4 + 3)
    if profondeur > 0:
        for i in range(nb_branches):
            angle_zp = 6.3 * i / nb_branches + random() * 3.14 / nb_branches
            angle_xp = 0.6 + random() * 0.6
            tronc.add(arbre(profondeur - 1, cylindre,
                angle_xp, angle_zp))

    return tronc

def creer_arbre(hauteur, profondeur, cylindre, position):
    transform = (translate(position)
            @ scale(hauteur)               # taille generale
            @ translate(0, -1, 0))
    tronc = Node(name='arbre', transform=transform)
    tronc.add(arbre(profondeur, cylindre))

    return tronc
