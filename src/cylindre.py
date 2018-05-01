from src.node import Node
from src.loaders import load_with_hierarchy

class Cylindre(Node):
    """ Very simple cylinder based on practical 2 load function """
    def __init__(self):
        super().__init__()
        self.add(load_with_hierarchy('arbre/cylinder.obj')[0])
