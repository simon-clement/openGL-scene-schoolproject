#!/usr/bin/env python3
"""
Python OpenGL practical application.
"""
# Python built-in modules
import os                           # os function, i.e. checking file status
import sys

# External, non built-in modules
import OpenGL.GL as GL              # standard Python OpenGL wrapper
import glfw                         # lean window system wrapper for OpenGL
import numpy as np                  # all matrix manipulations & OpenGL args
from itertools import cycle
from src.transform import translate, rotate, scale, vec, frustum, perspective, Trackball, identity
from src.interaction import GLFWTrackball
from src.shader import *


# ------------  Viewer class & window management ------------------------------
class Viewer:
    """ GLFW viewer window, with classic initialization & graphics loop """

    def __init__(self, width=640, height=480):

        # version hints: create GL window with >= OpenGL 3.3 and core profile
        self.vitesse_charge = 50
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.RESIZABLE, False)
        new_sample = 32
        glfw.window_hint(glfw.SAMPLES, new_sample) # MSAA: color buffer contains 4 subsamples per screen coordinate (all buffers size are increased by 4)
        self.win = glfw.create_window(width, height, 'Viewer', None, None)
        self.offset_time_for_loading = 0
        self.is_charging_geyser = False
        self.skybox = None

        self.trackball = GLFWTrackball(self.win)
        # make win's OpenGL context current; no OpenGL calls can happen before
        glfw.make_context_current(self.win)

        # register event handlers
        glfw.set_key_callback(self.win, self.on_key)

        # useful message to check OpenGL renderer characteristics
        print('OpenGL', GL.glGetString(GL.GL_VERSION).decode() + ', GLSL',
              GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION).decode() +
              ', Renderer', GL.glGetString(GL.GL_RENDERER).decode())

        # initialize GL by setting viewport and default render characteristics
        GL.glClearColor(0.1, 0.1, 0.1, 0.1)

        # GL.glEnable(GL.GL_CULL_FACE)
        GL.glEnable(GL.GL_MULTISAMPLE) # MSAA: Enable multisampling
        GL.glEnable(GL.GL_DEPTH_TEST)

        # compile and initialize shader programs once globally
        self.color_shader = Shader(COLOR_VERT, COLOR_FRAG)
        self.lambertian_shader = Shader(LAMBERTIAN_VERT, LAMBERTIAN_FRAG)
        self.geyser_shader = Shader(GEYSER_PARTICLE_VERT, GEYSER_PARTICLE_FRAG)
        self.skybox_shader = Shader(SKYBOX_VERT, SKYBOX_FRAG)
        self.ui_shader = Shader(UI_VERT, UI_FRAG)
        self.consigne_shader = Shader(CONSIGNE_VERT, CONSIGNE_FRAG)
        self.skinnning_shader = Shader(SKINNING_VERT, LAMBERTIAN_FRAG)
        self.arbre_shader = Shader(ARBRE_VERT, LAMBERTIAN_FRAG)
        self.herbe_shader = Shader(HERBE_VERT, HERBE_FRAG)
        self.shaders = {}
        self.shaders[GEYSER_SHADER_ID] = self.geyser_shader
        self.shaders[LAMBERTIAN_SHADER_ID] = self.lambertian_shader
        #  self.shaders[COLOR_SHADER_ID] = self.color_shader
        self.shaders[SKYBOX_SHADER_ID] = self.skybox_shader
        self.shaders[UI_SHADER_ID] = self.ui_shader
        self.shaders[CONSIGNE_SHADER_ID] = self.consigne_shader
        self.shaders[SKINNING_SHADER_ID] = self.skinnning_shader
        self.shaders[ARBRE_SHADER_ID] = self.arbre_shader
        self.shaders[HERBE_SHADER_ID] = self.herbe_shader
        self.particle_system = None
        self.elements_interacting = []
        self.elements_UI = []

        # initially empty list of object to draw
        self.drawables = []

    def run(self):
        """ Main render loop for this OpenGL window """
        while not glfw.window_should_close(self.win):
            # clear draw buffer
            ModelMat = np.matrix(rotate(angle=90))
            winsize = glfw.get_window_size(self.win)
            view = self.trackball.view_matrix()
            view_vec = self.trackball.view_vector()
            projection = self.trackball.projection_matrix(winsize)

            if self.skybox is None:
                GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
            else:
                GL.glClear(GL.GL_DEPTH_BUFFER_BIT)  # TODO enlever depth test pour le remettre
                view_skybox = self.trackball.view_matrix_skybox(100)
                #TODO mettre la distance ici
                self.skybox.draw(projection, view_skybox, ModelMat,
                              shaders=self.shaders, win=self.win,
                              view_vector=view_vec)

            # draw our scene objects
            for drawable in self.drawables:
                drawable.draw(projection, view, ModelMat,
                              shaders=self.shaders, win=self.win,
                              view_vector=view_vec)

            for elem_interact in self.elements_interacting:
                elem_interact.draw(projection, view, ModelMat,
                              shaders=self.shaders, win=self.win,
                              view_vector=view_vec)


            if self.is_charging_geyser:
                charge = min(self.vitesse_charge*(glfw.get_time() - self.offset_time_for_loading), 50)  / 50
            else:
                charge = 0

            for elem_ui in self.elements_UI:
                elem_ui.set_charge(charge)
                elem_ui.draw(projection, view, ModelMat,
                              shaders=self.shaders, win=self.win,
                              view_vector=view_vec)
            # flush render commands, and swap draw buffers
            glfw.swap_buffers(self.win)

            # Poll for and process events
            glfw.poll_events()

    def add(self, *drawables):
        """ add objects to draw in this window """
        self.drawables.extend(drawables)

    def set_skybox(self, drawable):
        self.skybox = drawable

    def add_element_interacting(self, elem_interact):
        self.elements_interacting += [elem_interact]

    def add_UI(self, mesh):
        self.elements_UI += [mesh]

    def on_key(self, _win, key, _scancode, action, _mods):
        """ 'Q' or 'Escape' quits """
        if action == glfw.PRESS or action == glfw.REPEAT:
            if key == glfw.KEY_ESCAPE or key == glfw.KEY_Q:
                glfw.set_window_should_close(self.win, True)
            if key == glfw.KEY_SPACE and action == glfw.PRESS:
                self.offset_time_for_loading = glfw.get_time()
                self.is_charging_geyser = True

        elif action == glfw.RELEASE:
            if key == glfw.KEY_SPACE and self.is_charging_geyser:
                self.is_charging_geyser = False
                charge = min(20 + self.vitesse_charge*(glfw.get_time() - self.offset_time_for_loading), 70)
                for elem_interact in self.elements_interacting:
                    elem_interact.new_geyser(charge)
