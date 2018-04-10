from src.transform import Trackball
import glfw                         # lean window system wrapper for OpenGL


class GLFWTrackball(Trackball):
    """ Use in Viewer for interactive viewpoint control """

    def __init__(self, win, bornes_zoom=(0.001, 190.),
                 bornes_rotate=(0.5, 1)):
        """ Init needs a GLFW window handler 'win' to register callbacks """
        super().__init__()
        self.angle_z = (bornes_rotate[0] + bornes_rotate[1])/2
        self.distance = (bornes_zoom[0] + bornes_zoom[1]) / 3
        self.bornes_zoom = bornes_zoom
        self.bornes_rotate = bornes_rotate
        self.mouse = (0, 0)
        glfw.set_cursor_pos_callback(win, self.on_mouse_move)
        glfw.set_scroll_callback(win, self.on_scroll)

    def on_mouse_move(self, win, xpos, ypos):
        """ Rotate on left-click & drag, pan on right-click & drag """
        old = self.mouse
        self.mouse = (xpos, glfw.get_window_size(win)[1] - ypos)
        if glfw.get_mouse_button(win, glfw.MOUSE_BUTTON_LEFT):
            self.drag(old, self.mouse, glfw.get_window_size(win))
            self.angle_z = min(max(self.bornes_rotate[0],
                                   self.angle_z), self.bornes_rotate[1])

    def on_scroll(self, win, _deltax, deltay):
        """ Scroll controls the camera distance to trackball center """
        self.zoom(deltay, glfw.get_window_size(win)[1])
        if self.bornes_zoom[0] > self.distance:
            self.distance = self.bornes_zoom[0]
        elif self.bornes_zoom[1] < self.distance:
            self.distance = self.bornes_zoom[1]
