class Cylinder(Node):
    """ Very simple cylinder based on practical 2 load function """
    def __init__(self):
        super().__init__()
        self.add(*load('cylinder.obj'))
