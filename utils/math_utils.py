import math


def mobility(entity):
    raw = 1.0 / (entity.mass * (1.0 + entity.radius * 0.1))
    return max(0.5, min(1.0, raw))


def edge_damping(x, p=2.0):
    core = 4.0 * x * (1.0 - x)
    return max(0.0, core) ** p


def sigmoid01(x, k=10, x0=0.5):
    return 1 / (1 + math.exp(-k * (x - x0)))
