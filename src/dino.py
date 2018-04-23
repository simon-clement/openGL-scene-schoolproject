#!/usr/bin/env python3
"""
Python OpenGL dinosaurus : sweet and flying with geysers
"""

import glfw                         # lean window system wrapper for OpenGL
from src.transform import rotate, translate

class Dino:
    """This class should make the dino fly :3 """
    def __init__(self, node_dino):
        self.node_dino = node_dino
        self.pos_z = 0
        self.angle = 0
        self.vitesse_z = 0
        self.offset_animation = glfw.get_time() - 10
        self.time_offset = glfw.get_time()

    def draw(self, projection, view, model, **param):
        """just draw the node, passing all arguments"""
        # --- recuperation du temps passe
        newt = glfw.get_time()
        dt = newt - self.time_offset
        self.time_offset = newt

        # --- actualisation des donnees
        self.vitesse_z -= 98.1 * dt
        self.pos_z += self.vitesse_z * dt
        if self.pos_z < 0:
            self.vitesse_z = 0
            self.pos_z = 0
        else:
            self.angle += 30 * dt

        transform = rotate(axis=(0,1,0), angle=self.angle) @ translate(0,self.pos_z,0)
        model = model @ transform
        self.node_dino.draw(projection, view, model,
                            time=(self.time_offset - self.offset_animation)*3, **param)

    def new_geyser(self, charge):
        """ fait voler le dino si il est au sol..."""
        # en vrai faudra faire une fonction qui ajoute de la vitesse
        # en fonction de sa position
        self.vitesse_z += charge / (0.1 * self.pos_z + 1)
        self.offset_animation = glfw.get_time()
        # TODO reset l'animation du dino
