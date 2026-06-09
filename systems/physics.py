import math

import config


def apply_absorption(entities, dt):
    k = 2

    for i in range(len(entities)):
        for j in range(i + 1, len(entities)):
            a = entities[i]
            b = entities[j]
            dx = a.pos[0] - b.pos[0]
            dy = a.pos[1] - b.pos[1]
            distance = math.sqrt(dx**2 + dy**2)
            if distance == 0:
                continue

            if a.radius > b.radius:
                big, small = a, b
            elif b.radius > a.radius:
                big, small = b, a
            else:
                continue

            if distance + small.radius > big.radius:
                continue

            mass_factor = abs((big.mass - small.mass)) / max(big.mass, small.mass)
            radius_factor = small.radius / big.radius
            overlap = big.radius - distance

            transfer_rate = k * overlap * mass_factor * radius_factor

            dm = transfer_rate * dt
            dm = max(0, min(dm, small.mass))

            small.mass -= dm
            big.mass += dm
            small.radius -= dm
            big.radius += dm


def apply_forces(entities, dt):
    eps = 1e-6

    visc_min = 2.0
    visc_max = 20.0

    def smoothstep(x):
        x = 0.0 if x < 0.0 else 1.0 if x > 1.0 else x
        return x * x * (3.0 - 2.0 * x)

    n = len(entities)

    for i in range(n):
        a = entities[i]
        for j in range(i + 1, n):
            b = entities[j]

            dx = b.pos[0] - a.pos[0]
            dy = b.pos[1] - a.pos[1]
            dist2 = dx * dx + dy * dy
            if dist2 <= eps:
                continue

            dist = math.sqrt(dist2)
            sum_r = a.radius + b.radius
            overlap = sum_r - dist
            if overlap <= 0.0:
                continue

            small, big = (a, b) if a.radius <= b.radius else (b, a)
            inside_depth = big.radius - (dist + small.radius)

            band = 0.15 * small.radius + eps
            inside = smoothstep((inside_depth + band) / (2.0 * band))

            if inside <= 0.0:
                continue

            visc = visc_min + (visc_max - visc_min) * inside * inside
            relx = a.velocity[0] - b.velocity[0]
            rely = a.velocity[1] - b.velocity[1]

            fx = -visc * inside * relx
            fy = -visc * inside * rely

            a.force[0] += fx
            a.force[1] += fy
            b.force[0] -= fx
            b.force[1] -= fy


def apply_dynamics(entities, dt):
    for e in entities:
        inv_mass = 1 / max(e.mass, 0.1)

        ax = e.force[0] * inv_mass
        ay = e.force[1] * inv_mass

        e.velocity[0] += ax * dt
        e.velocity[1] += ay * dt

        e.force = [0, 0]


def apply_boundaries(entities, dt):
    w, h = config.WIDTH, config.HEIGHT

    for entity in entities:
        if entity.pos[0] - entity.radius < 0:
            entity.pos[0] = entity.radius
            entity.velocity[0] *= -0.5
        elif entity.pos[0] + entity.radius > w:
            entity.pos[0] = w - entity.radius
            entity.velocity[0] *= -0.5

        if entity.pos[1] - entity.radius < 0:
            entity.pos[1] = entity.radius
            entity.velocity[1] *= -0.5
        elif entity.pos[1] + entity.radius > h:
            entity.pos[1] = h - entity.radius
            entity.velocity[1] *= -0.5


def apply_movement(entities, dt):
    for entity in entities:
        entity.velocity[0] *= (1 - config.FRICTION * dt)
        entity.velocity[1] *= (1 - config.FRICTION * dt)

        entity.pos[0] += entity.velocity[0] * dt
        entity.pos[1] += entity.velocity[1] * dt


def filter_dead_entities(entities):
    return [e for e in entities if e.mass > 0.1 and e.radius > 0.1]
