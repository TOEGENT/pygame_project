import config
import math
import random
from entities.intent import Intent
from utils import smooth_normal
class Ball:
    def __init__(self,pos: tuple,color,mass=None,team=None):
        self.pos = pos
        self.color = color
        self.view_point=(0,0)
        self.mass=mass or config.MINIMUM_MASS
        self.team=team if team is not None else None
        self.lost_mass_to_spawn = 0
        self.is_eaten_by=set()
        self.eats=set()
        self.old_mass=self.mass
        self.mass_before_decay = self.mass
        self.old_pos = self.pos
        self.smooth_view = self.view_point
        self.intents=[]
        self.smooth_intents=self.intents
        self.total_intent = Intent((0,0),None)
        self.smooth_total_intent = self.total_intent
        self.wander_angle = random.uniform(0,2*math.pi)
        self.ai_split_cooldown = 0

            

    @property
    def radius(self):
        return math.sqrt(self.mass)
    
    @property
    def old_radius(self):
        return math.sqrt(self.old_mass)

    @property
    def speed(self):
        return config.BALL_SPEED_FACTOR * math.sqrt(self.radius) / self.radius
    

    @property
    def normal(self):
        self.smooth_view = smooth_normal.smooth_add_pos(self.smooth_view,self.view_point)
        dx = self.smooth_view[0]-self.pos[0]
        dy = self.smooth_view[1]-self.pos[1]
        dist = math.hypot(dx,dy)
        if dist<1:
            return (0,0)
        return (dx/dist,dy/dist)
    
