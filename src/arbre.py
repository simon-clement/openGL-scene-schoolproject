#!/usr/bin/env python3
"""
Python OpenGL dinosaurus : sweet and flying with geysers
"""

import glfw                         # lean window system wrapper for OpenGL
from src.transform import rotate, translate, scale
from src.node import Node
from src.cylindre import Cylindre
import math
from random import random

def faire_pousser_sur(tronc, branches_restantes):
    branches_restantes -= 1
    hauteur = tronc.hauteur / 3.

    for i in range(2):
        transform = (translate(0, 0, 0)     # orientation des branches
                @ scale(hauteur)            # diminuer la taille de la branche
                @ translate(0, 0, 0))       # pour placer au sommet du tronc
        branche = Node(transform=transform, color=(.65, .40, .15))
        tronc.add(branche)
        
        if branches_restantes < 0:
            faire_pousser_sur(branche, branches_restantes)
    

class Arbre:
    """Class of tree"""
    def __init__(self):
        self.hauteur = 10

        transform = (translate(0, 0, 0)
                @ scale(self.hauteur)
                @ translate(0, 0, 0))
        tronc = Node(name='arbre', transform=transform, color=(167, 103, 38))
        tronc.add(Cylindre())

        faire_pousser_sur(tronc, 1)

    def draw(self, projection, view, model, **param):
        """just draw the node, passing all arguments"""
        self.tronc.draw(projection, view, model, **param)

class Poubelle:
    """This class should make the ptero fly :3 """
    def __init__(self, node_dino):
        self.node_dino = node_dino
        self.angle = 0
        self.distance = 40
        self.hauteur = 20
        self.time_offset = glfw.get_time()

    def draw(self, projection, view, model, **param):
        """just draw the node, passing all arguments"""
        # --- recuperation du temps passe
        newt = glfw.get_time()
        dt = newt - self.time_offset
        self.time_offset = newt

        # --- actualisation des donnees
        self.angle += 20 * dt
        time_in_animation = self.time_offset%5
        real_height = self.hauteur + 7*math.cos(-0.5+time_in_animation * 2*3.1415/5)
        #(3 - time_in_animation) 
        #* (1 - 5/2 * (time_in_animation >= 3))*3

        transform = rotate(axis=(0,1,0), angle=self.angle) @ translate(self.distance,real_height,0)
        model = model @ transform
        self.node_dino.draw(projection, view, model,
                            time=time_in_animation, **param)

