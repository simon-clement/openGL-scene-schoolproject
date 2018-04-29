import numpy as np                  # all matrix manipulations & OpenGL args
import glfw                         # lean window system wrapper for OpenGL
from src.transform import identity
from src.animation import TransformKeyFrames

# ------------  node classes ------------------------------------------
class Node:
    """ Scene graph transform and parameter broadcast node """
    def __init__(self, name='', children=(), transform=np.identity(4), **param):
        self.transform, self.param, self.name = transform, param, name
        self.children = list(iter(children))

    def add(self, *drawables):
        """ Add drawables to this node, simply updating children list """
        self.children.extend(drawables)

    def draw(self, projection, view, model, time=None, **param):
        """ Recursive draw, passing down named parameters & model matrix. """
        # merge named parameters given at initialization with those given here
        param = dict(param, **self.param)
        model = model @ self.transform
        for child in self.children:
            child.draw(projection, view, model, time=time, **param)


class KeyFrameControlNode(Node):
    """ Place node with transform keys above a controlled subtree """
    def __init__(self, translate_keys, rotate_keys, scale_keys, **kwargs):
        super().__init__(**kwargs)
        self.keyframes = TransformKeyFrames(translate_keys, rotate_keys, scale_keys)

    def draw(self, projection, view, model, time=None, **param):
        """ When redraw requested, interpolate our node transform from keys """
        if time is None:
            time = glfw.get_time()
        self.transform = self.keyframes.value(time)
        super().draw(projection, view, model, time=time, **param)


# -------- Skinning Control for Keyframing Skinning Mesh Bone Transforms ------
class SkinningControlNode(Node):
    """ Place node with transform keys above a controlled subtree """
    def __init__(self, *keys, **kwargs):
        super().__init__(**kwargs)
        self.keyframes = TransformKeyFrames(*keys) if keys[0] else None
        self.world_transform = identity()

    def draw(self, projection, view, model, time=None, **param):
        """ When redraw requested, interpolate our node transform from keys """
        if self.keyframes:  # no keyframe update should happens if no keyframes
            if time is None:
                time = glfw.get_time()
            self.transform = self.keyframes.value(time)

        # store world transform for skinned meshes using this node as bone
        self.world_transform = model @ self.transform

        # default node behaviour (call children's draw method)
        super().draw(projection, view, model, time=time, **param)


