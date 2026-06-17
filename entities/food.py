import math

class Food:
    def __init__(self,pos: tuple):
        self.pos = pos
        self.mass = 1
        self.is_eaten = False
        self.team = None
        self.color = None
    @property
    def radius(self):
        return math.sqrt(self.mass)