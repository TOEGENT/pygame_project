class Ball:
    def __init__(self, color, pos, radius, mass):
        self.color = color
        self.pos = pos
        self.radius = radius
        self.mass = mass
        self.velocity = [0, 0]
        self.force = [0, 0]
