import math


class TeamBlob:
    def __init__(self, pos, mass, team):
        self.pos = pos
        self.mass = mass
        self.team = team

    @property
    def radius(self):
        return math.sqrt(self.mass)
