import config
import math
class Ball:
    def __init__(self,pos: tuple,color,mass=None):
        self.pos = pos
        self.color = color
        self.view_point=(0,0)
        self.mass=mass or config.MINIMUM_MASS
        self.is_alive = True
        self.lost_mass_to_spawn = 0

    @property
    def radius(self):
        return math.sqrt(self.mass)
    
    @property
    def speed(self):
        return math.sqrt(self.radius)/self.radius
    
    @property
    def normal(self):
        dx = self.view_point[0] - self.pos[0]
        dy = self.view_point[1] - self.pos[1]
        distance = (dx**2 + dy**2)**0.5
        if distance==0:
            return (0,0)
        return (dx/distance,dy/distance)