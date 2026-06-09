import math
import random

import config
from utils.math_utils import mobility


def update_ai(entities, dt):
    for i in range(0, len(entities)):
        if entities[i] == entities[0]:
            continue

        total_force_x = 0
        total_force_y = 0
        a = entities[i]

        for j in range(0, len(entities)):
            b = entities[j]
            if a == b:
                continue

            dx = a.pos[0] - b.pos[0]
            dy = a.pos[1] - b.pos[1]
            distance = max(0.1, math.sqrt(dx**2 + dy**2))

            if distance > a.radius * 15 + b.radius:
                total_force_x += random.uniform(-1, 1) * 0.3
                total_force_y += random.uniform(-1, 1) * 0.3
                continue

            nx = dx / distance
            ny = dy / distance

            if a.radius > b.radius:
                attraction = (b.mass / a.mass) * 0.5
                distance_influence = max(0, 1.0 - distance / (a.radius * 20))
                force = attraction * distance_influence
                total_force_x -= force * nx
                total_force_y -= force * ny
            else:
                threat = (b.mass / a.mass) * 0.7
                distance_influence = max(0, 1.0 - distance / (a.radius * 20))
                force = threat * distance_influence
                total_force_x += force * nx
                total_force_y += force * ny

        speed_mult = (config.MAX_RADIUS / max(a.radius, 1)) * 0.5
        speed_mult = max(0.1, min(2.0, speed_mult))

        a.force[0] += total_force_x * config.ACCELERATION * speed_mult * mobility(a)
        a.force[1] += total_force_y * config.ACCELERATION * speed_mult * mobility(a)
