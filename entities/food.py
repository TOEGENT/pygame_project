import math

class Food:
    def __init__(self,pos: tuple):
        self.pos = pos
        self.mass = 1
        self.team = None
        self.color = None
        self.is_eaten_by = set()
        self.is_alive=True
    @property
    def radius(self):
        return math.sqrt(self.mass)