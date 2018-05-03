#!/usr/bin/env python3
"""
Python OpenGL dinosaurus : sweet and flying with geysers
"""

from src.transform import rotate, translate, scale
from src.node import Node
from src.cylindre import Plan

def herbe(plan, angle_z=0, ind=3):
    transform = (rotate(axis=(0, 0, 1), angle=(angle_z)))
    baseH = Node(name='herbe', transform=transform)
    baseH.add(plan)
    if (ind > 0):
        ind -= 1
        baseH.add(herbe(plan, 60, ind))
    return baseH

def creer_herbe(plan, taille, position, angle_z=0):
    transform = (translate(position) @ rotate(axis=(0, 1, 0), angle=(angle_z)) @ rotate(axis=(1, 0, 0), angle=(90)) @ scale(taille))
    baseH = Node(name='arbre', transform=transform)
    baseH.add(herbe(plan))
    return baseH
